# -*- coding: utf-8 -*-

import sys
import threading
import asyncio
from http_server import app
from websocket_handler import main as websocket_main  # 修改导入路径
import dylr.core.app as app_core

def start_websocket_server():
    asyncio.run(websocket_main())

def main():
    # 启动WebSocket服务器
    websocket_server_thread = threading.Thread(target=start_websocket_server)
    websocket_server_thread.setDaemon(True)
    websocket_server_thread.start()

    # 启动HTTP服务器
    http_server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    http_server_thread.setDaemon(True)
    http_server_thread.start()

    # 启动核心应用
    run_cli()

def run_cli():
    app_core.init(False)

if __name__ == '__main__':
    main()

