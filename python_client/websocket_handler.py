import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None
        self.on_message_callback = None  # 用于处理接收到的消息

    async def connect(self):
        self.connection = await websockets.connect(self.uri)
        logger.info("WebSocket connected.")

        # 启动接收消息的协程
        asyncio.create_task(self.receive_messages())

    async def send(self, message):
        if self.connection:
            await self.connection.send(json.dumps(message))
            logger.info(f"Sent message: {message}")

    async def receive_messages(self):
        while True:
            try:
                message = await self.connection.recv()
                logger.info(f"Received message: {message}")
                if self.on_message_callback:
                    await self.on_message_callback(json.loads(message))
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed.")
                break

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("WebSocket closed.")

    def set_on_message_callback(self, callback):
        """设置接收到消息时的回调函数"""
        self.on_message_callback = callback 