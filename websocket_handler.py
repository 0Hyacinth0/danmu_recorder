import asyncio
from socket import MSG_ERRQUEUE
import websockets
import json
from dylr.core import record_manager, monitor, dy_api
from dylr.core.room import Room
from dylr.util import logger
from dylr.core.danmu_recorder import DanmuRecorder

connected_clients = set()
room_listeners = {}
client_room = {}

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')
                room_id = str(data.get('room_id'))  # 确保房间号是字符串
                if action == 'start_recording':
                    room_name = data.get('room_name')
                    if not room_id:
                        await websocket.send(json.dumps({'error': '房间号是必需的'}))
                        continue

                    if not room_name or room_name == 'Unknown':
                        # 如果房间名称未知，通过API获取房间名称
                        room_info = dy_api.get_live_state_json(room_id)
                        if room_info:
                            room_name = room_info.get('owner', {}).get('nickname', '未知')

                    room = record_manager.get_room(room_id)
                    if room is None:
                        room = Room(room_id, room_name, True, True, False)
                        record_manager.rooms.append(room)
                        logger.info_and_print(f'添加新房间: {room_name}({room_id})')

                    monitor.check_room(room)
                    room_listeners[room_id] = websocket
                    client_room[websocket] = room_id
                    await websocket.send(json.dumps({'message': f'开始录制房间: {room_name}({room_id})'}))
                    asyncio.create_task(monitor_room(room_id, websocket))
                    asyncio.create_task(send_danmu_to_client(room_id, websocket))
                    print(f"已添加到 client_room: {websocket} -> {room_id}")
                elif action == 'stop_recording':
                    if room_id in room_listeners:
                        del room_listeners[room_id]
                        await websocket.send(json.dumps({'message': f'停止录制房间: {room_id}'}))
                    else:
                        await websocket.send(json.dumps({'error': f'房间: {room_id} 没有正在录制'}))
                elif action == 'heartbeat':
                    # 处理心跳消息，发送最新的弹幕信息
                    await websocket.send(json.dumps({'message': '心跳消息已接收'}))
                elif action == 'get_room_listeners':
                    room_listeners_data = {room_id: str(ws) for room_id, ws in room_listeners.items()}
                    await websocket.send(json.dumps({'room_listeners': room_listeners_data}))
                elif action == 'send_danmu':
                    content = data.get('content')
                    if room_id in room_listeners:
                        danmu_data = {
                            'content': content,
                            'name': '系统消息',
                            'msg_type': 0,
                            'room_id': room_id
                        }
                        await room_listeners[room_id].send(json.dumps(danmu_data))
                        print(f"获取弹幕 {room_id}: {content}")
                    else:
                        await websocket.send(json.dumps({'error': f'房间: {room_id} 没有正在录制'}))
                else:
                    await websocket.send(json.dumps({'error': '未知操作'}))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({'error': '无效的 JSON'}))
            except Exception as e:
                await websocket.send(json.dumps({'error': str(e)}))
    finally:
        connected_clients.remove(websocket)

async def send_danmu_to_client(room_id, websocket):
    recorder = DanmuRecorder(record_manager.get_room(room_id), room_id)
    recorder.start()
    while room_id in room_listeners:
        try:
            danmu_data = await asyncio.get_event_loop().run_in_executor(None, MSG_ERRQUEUE.get)
            await websocket.send(json.dumps(danmu_data))
        except Exception as e:
            print(f"发送弹幕到客户端时出错: {str(e)}")
            break

async def monitor_room(room_id, websocket):
    while room_id in room_listeners:
        room = record_manager.get_room(room_id)
        if room is None:
            break

        if not dy_api.is_going_on_live(room):
            del room_listeners[room_id]
            await websocket.send(json.dumps({'message': f'房间: {room_id} 直播已结束'}))
            break

        await asyncio.sleep(10)  # 每10秒检查一次直播状态

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
