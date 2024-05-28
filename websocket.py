# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 14:40
# software: PyCharm
import asyncio
import concurrent.futures
import json
import nest_asyncio
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from response import Status
from utils.logger import logger
from message_handler import MessageHandler

executor = concurrent.futures.ThreadPoolExecutor()

app = FastAPI()
logger.basicConfig(20)

nest_asyncio.apply()


class ConnectionManager:
    """
    连接管理器
    """
    SESSION_UUID = "sessionUuid"

    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket):
        # 等待连接
        await ws.accept()
        logger.info("连接成功")

    async def save_session(self, json_data, ws: WebSocket):
        # 如果json_data中没有sessionUuid的key 则返回错误
        if self.SESSION_UUID not in json_data:
            await ws.send_text(f"{self.SESSION_UUID} is required")
            await ws.close()
        # 如果active_connections中不存在则添加
        if json_data[self.SESSION_UUID] not in self.active_connections:
            session_uuid = json_data[self.SESSION_UUID]
            self.active_connections[session_uuid] = ws
            logger.info(f"用户{session_uuid}建立连接")

    def disconnect(self, ws: WebSocket):
        session_uuid = [k for k, v in manager.active_connections.items() if v == ws]
        if session_uuid:
            self.active_connections.pop(session_uuid[0])
            logger.info(f"用户{session_uuid[0]}断开连接")

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        # 发送个人消息
        await ws.send_text(message)

    async def broadcast(self, message: str):
        # 广播消息
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/1action")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    message_handler = MessageHandler()

    async def process_messages(data):
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            logger.warning("接收到的数据不是有效的JSON格式，跳过处理。")
            return

        await manager.save_session(json_data, websocket)
        logger.info(f"接收到-->{json_data}")

        # 在全局线程池中处理消息
        output = await asyncio.to_thread(message_handler.handle_message, json_data)
        if output is None:
            return
        # 发送处理完的消息
        await manager.send_personal_message(output.to_json(), websocket)
        output.status = Status.END
        # 发送处理完的消息
        await manager.send_personal_message(output.to_json(), websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # 将接收消息放入后台处理
            asyncio.create_task(process_messages(data))

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
        logger.info(f"仍活跃的连接-->{manager.active_connections}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
