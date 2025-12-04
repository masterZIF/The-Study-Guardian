import cv2
import mediapipe as mp
import numpy as np
import time

class VideoCamera(object):
    def __init__(self):
        # 0 代表默认摄像头
        self.video = cv2.VideoCapture(0) 
        
        # === 关键修改：强制设置低分辨率以保证流畅度 ===
        # 很多摄像头默认开启 1080p 或 4K，导致 Python 处理不过来从而掉帧
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.video.set(cv2.CAP_PROP_FPS, 30)
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.status = "Normal" 
        self.neck_inclination = 0 
        self.start_time = time.time()

    def __del__(self):
        self.video.release()

    def calculate_angle(self, a, b, c):
        a = np.array(a) 
        b = np.array(b) 
        c = np.array(c) 
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            # 如果读取失败，返回一个黑色空图片防止报错
            return None

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = self.pose.process(image_rgb)

        image.flags.writeable = True
        h, w, _ = image.shape

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # 获取坐标
            nose = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x, landmarks[self.mp_pose.PoseLandmark.NOSE.value].y]
            l_ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y * h]
            l_shldr = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            
            # 驼背判定
            vertical_point = [l_shldr[0], l_shldr[1] + 100] 
            self.neck_inclination = self.calculate_angle(l_ear, l_shldr, vertical_point)

            # 状态判定
            if self.neck_inclination < 150: 
                self.status = "Warning: Slouching!"
                color = (0, 0, 255) # 红色
            else:
                self.status = "Normal"
                color = (0, 255, 0) # 绿色

            # 绘制文字
            cv2.putText(image, self.status, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            cv2.putText(image, f"Neck Angle: {int(self.neck_inclination)}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            # 绘制骨骼
            self.mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_data(self):
        return {
            "status": self.status,
            "angle": int(self.neck_inclination),
            "timestamp": time.strftime("%H:%M:%S")
        }