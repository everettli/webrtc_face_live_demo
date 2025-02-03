import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connected_clients = set()

async def handler(websocket, path):
    # 注册新连接
    connected_clients.add(websocket)
    logger.info("New client connected.")

    try:
        async for message in websocket:
            logger.info(f"Received message: {message}")
            # 这里可以处理接收到的消息并广播给所有连接的客户端
            for client in connected_clients:
                if client != websocket:  # 不发送给发送者
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected.")
    finally:
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handler, "127.0.0.1", 8088)
    logger.info("WebSocket server started on ws://127.0.0.1:8088/ws")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 