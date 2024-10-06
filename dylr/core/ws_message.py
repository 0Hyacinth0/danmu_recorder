from websocket_server import WebsocketServer
class Ws():
    def __init__(self):
        pass


    def new_client(self,client, server):
        print('xiaoxi')

    # 接收到客户端消息时触发
    def message_received(self,client, server, message,mes=None):
        print('mes',mes)
        server.send_message_to_all(f'111:2222:333333{mes}')

    # 客户端关闭连接时触发
    def client_left(self,client, server):
        print("Client(%d) disconnected" % client["id"])

# 建立 WebSocketServer 对象，监听 9001 端口
if __name__ == '__main__':
    ws=Ws()
    server = WebsocketServer('0.0.0.0',9002)
    server.set_fn_new_client(ws.new_client)
    server.set_fn_message_received(ws.message_received)
    server.set_fn_client_left(ws.client_left)

    # 启动服务器
    server.run_forever()
