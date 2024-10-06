import _thread
import gzip
import os
import time
import traceback
import websocket
import queue
import json
from google.protobuf import json_format
from dylr.core import dy_api, app, record_manager
from dylr.core.dy_protocol import PushFrame, Response, RoomUserSeqMessage, ChatMessage, GiftMessage, MemberMessage, SocialMessage
from dylr.util import logger, cookie_utils
import threading
import ssl
import pymysql

msg_queue = queue.Queue()
clients = []
client_room = {}

global flag
flag = True

class DanmuRecorder:
    def __init__(self, room, room_real_id, start_time=None):
        self.room = room
        self.room_id = room.room_id
        self.room_name = room.room_name
        self.room_real_id = room_real_id
        self.start_time = start_time
        self.ws = None
        self.stop_signal = False
        self.danmu_amount = 0
        self.last_danmu_time = 0
        self.retry = 0
        self.ws_server = None

    def start(self):
        global flag
        if flag:
            # self.start_ws()  # 移除对start_ws方法的调用
            pass
        flag = False
        if self.start_time is None:
            self.start_time = time.localtime()
        self.start_time_t = int(time.mktime(self.start_time))
        logger.info_and_print(f'开始录制2 {self.room_name}({self.room_id}) 的弹幕')
        self.ws = websocket.WebSocketApp(
            url=dy_api.get_danmu_ws_url(self.room_id, self.room_real_id),
            header=dy_api.get_request_headers(),
            cookie=cookie_utils.cookie_cache,
            on_message=self._onMessage,
            on_error=self._onError,
            on_close=self._onClose,
            on_open=self._onOpen,
        )
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def _onMessage(self, ws: websocket.WebSocketApp, message: bytes):
        wssPackage = PushFrame()
        wssPackage.ParseFromString(message)
        decompressed = gzip.decompress(wssPackage.payload)
        payloadPackage = Response()
        payloadPackage.ParseFromString(decompressed)

        # 发送ack包
        if payloadPackage.needAck:
            obj = PushFrame()
            obj.payloadType = 'ack'
            obj.logid = wssPackage.logid
            obj.payloadType = payloadPackage.internalExt
            data = obj.SerializeToString()
            ws.send(data, websocket.ABNF.OPCODE_BINARY)
        # 处理消息
        for msg in payloadPackage.messagesList:
            if msg.method == 'WebcastChatMessage':
                chatMessage = ChatMessage()
                chatMessage.ParseFromString(msg.payload)
                data = json_format.MessageToDict(chatMessage, preserving_proto_field_name=True)
                now = time.time()
                second = now - self.start_time_t
                self.danmu_amount += 1
                self.last_danmu_time = now
                try:
                    # 打印弹幕信息到控制台
                    print(str(self.room_id) + ':' + data['user']['nickName'] + ':' + data['content'])
                    # 发送弹幕信息给WebSocket客户端
                    danmu_data = {
                        'content': data['content'],
                        'name': data['user']['nickName'],
                        'msg_type': 0,
                        'room_id': self.room_id
                    }
                    msg_queue.put(danmu_data)
                    for key, value in client_room.items():
                        if value == self.room_id:
                            key.send(json.dumps(danmu_data))
                            print('已发送', danmu_data)
                        else:
                            print(f"没有匹配的房间ID {self.room_id} 在 client_room 中")
                except Exception as e:
                    print(time.strftime('%Y-%m-%d %H:%M:%S') + ' 入库失败')
                    print(f"错误详情: {str(e)}")
                    traceback.print_exc()

    def _heartbeat(self, ws: websocket.WebSocketApp):
        t = 9
        while True:
            if app.stop_all_threads or self.stop_signal:
                ws.close()
                break
            if not ws.keep_running:
                break
            if t % 10 == 0:
                obj = PushFrame()
                obj.payloadType = 'hb'
                data = obj.SerializeToString()
                ws.send(data, websocket.ABNF.OPCODE_BINARY)
                if self.retry < 1 and self.danmu_amount == 0 and t > 6000000:
                    ws.close()
                    logger.warning_and_print(f'{self.room_name}({self.room_id}) 无法获取弹幕，正在重试({self.retry + 1})')
                now = time.time()
                if t > 30 and now - self.last_danmu_time > 3600000:
                    if not dy_api.is_going_on_live(self.room):
                        ws.close()
            t += 1
            time.sleep(1)

    def _onError(self, ws, error):
        logger.error_and_print(f'[onError] {self.room_name}({self.room_id})弹幕录制抛出一个异常')
        logger.error_and_print(traceback.format_exc())

    def _onClose(self, ws, a, b):
        logger.info_and_print(f'{self.room_name}({self.room_id}) 弹幕录制结束')
        if app.stop_all_threads or self.stop_signal:
            return
        if self.retry < 3 and dy_api.is_going_on_live(self.room):
            self.retry += 1
            self.start_time = None
            time.sleep(1)
            self.start()
