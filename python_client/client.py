import asyncio
import json
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCIceCandidate
from websocket_handler import WebSocketClient
from face_detector import FaceDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebRTCClient:
    def __init__(self, websocket_url):
        self.pc = None
        self.ws_client = WebSocketClient(websocket_url)
        self.face_detector = FaceDetector()
        self.data_channel = None

    async def connect(self):
        logger.info("Connecting to WebSocket...")
        await self.ws_client.connect()
        
        # 设置消息处理回调
        self.ws_client.set_on_message_callback(self.handle_message)
        
        logger.info("WebSocket connected.")


    def handle_video_track(self, track):
        logger.info("Handling video track...")
        detector_track = self.face_detector.create_detection_track(track)
        self.pc.addTrack(detector_track)
        logger.info("Video track added to RTCPeerConnection.")


    async def close(self):
        logger.info("Closing RTCPeerConnection...")
        if self.pc:
            await self.pc.close()
            logger.info("RTCPeerConnection closed.")
        if self.ws_client:
            await self.ws_client.close()
            logger.info("WebSocket closed.")
    
    async def handle_message(self, message):
        if message['type'] == 'offer':
            await self.handle_offer(message)
        elif message['type'] == 'answer':
            await self.handle_answer(message)
        elif message['type'] == 'candidate':
            await self.handle_candidate(message)
        elif message['type'] == 'close':
            await self.handle_close()

    async def handle_offer(self, offer):
        logger.info("Handling offer...")
        self.pc = RTCPeerConnection()

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            self.data_channel = channel
            logger.info("Data channel created.")

            @channel.on("message")
            def on_message(message):
                logger.info(f"Received message: {message}")

        @self.pc.on("track")
        def on_track(track):
            logger.info(f"Track received: {track.kind}")
            if track.kind == "video":
                self.handle_video_track(track)

        try:
            await self.pc.setRemoteDescription(RTCSessionDescription(sdp=offer['sdp'], type=offer['type']))
            logger.info("Remote description set successfully.")
            logger.info("Creating answer...")
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            logger.info("Answer created and set as local description.")
            await self.ws_client.send({
                'type': 'answer',
                'sdp': answer.sdp,
            })
            logger.info("Answer sent successfully.")
        except Exception as e:
            logger.error(f"Error handling offer: {e}")

    async def handle_answer(self, answer):
        logger.info("Handling answer...")
        try:
            await self.pc.setRemoteDescription(RTCSessionDescription(sdp=answer["sdp"], type=answer["type"]))
            logger.info("Remote description set successfully.")
        except Exception as e:
            logger.error(f"Error handling answer: {e}")

    async def handle_candidate(self, message):
        logger.info("Handling ICE candidate...")
        candidate_info = message['candidate']  # 提取候选者详细信息  
        
        # 提取ICE候选者字符串和其他字段  
        candidate_string = candidate_info['candidate']  
        sdp_mid = candidate_info.get('sdpMid')  
        sdp_mline_index = candidate_info.get('sdpMLineIndex')  
        
        # 解析候选者字符串  
        parts = candidate_string.split()  
        if len(parts) < 8:  
            raise ValueError("Invalid candidate format")  

        # 提取候选者各个参数  
        foundation = parts[0]  
        component = int(parts[1])  
        protocol = parts[2]  
        priority = int(parts[3])  
        ip = parts[4]  
        port = int(parts[5])  
        type_candidate = parts[7]  # types: host, srflx, relay 等  
        
        # 创建RTCIceCandidate  
        ice_candidate = RTCIceCandidate(  
            foundation=foundation,  
            component=component,  
            protocol=protocol,  
            priority=priority,  
            ip=ip,  
            port=port,  
            type=type_candidate,  
            sdpMid=sdp_mid,  
            sdpMLineIndex=sdp_mline_index  
        ) 
        await self.pc.addIceCandidate(ice_candidate)
        logger.info("ICE candidate added.")

    async def handle_close(self):
        logger.info("Handling close...")
        await self.close()
    

async def main():
    client = WebRTCClient("ws://127.0.0.1:8088/ws")
    try:
        await client.connect()
        # Main application logic here
        await asyncio.sleep(3600)  # Keep connection alive
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 