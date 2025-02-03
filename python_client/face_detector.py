import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import logging
logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self):
        # 使用OpenCV预训练的人脸检测分类器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # 加载要显示的人脸图片
        self.replacement_face_image = cv2.imread('/Users/everett/Desktop/doge.jpg')  # 替换为实际路径
        self.replacement_face_image = cv2.resize(self.replacement_face_image, (100, 100))  # 调整大小

    def create_detection_track(self, input_track):
        return FaceDetectionVideoStreamTrack(self.face_cascade, input_track, self.replacement_face_image)

class FaceDetectionVideoStreamTrack(VideoStreamTrack):
    def __init__(self, face_cascade, input_track, replacement_face_image):
        super().__init__()
        self.face_cascade = face_cascade
        self.input_track = input_track
        self.replacement_face_image = replacement_face_image
        self.processing = False

    async def recv(self):
        logger.info("recv")
        frame = await self.input_track.recv()
        
        if not self.processing:
            self.processing = True
            # Convert frame to numpy array for OpenCV processing
            img = frame.to_ndarray(format="bgr24")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Replace detected faces with the replacement image
            for (x, y, w, h) in faces:
                # Resize the replacement image to fit the detected face area
                resized_face_image = cv2.resize(self.replacement_face_image, (w, h))
                # Replace the face area in the original image
                img[y:y+h, x:x+w] = resized_face_image
            
            # Convert back to VideoFrame
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            
            self.processing = False
            return new_frame
        
        return frame 