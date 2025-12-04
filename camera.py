import cv2
import mediapipe as mp
import numpy as np
import time

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0) # 0 代表默认摄像头
        
        # 初始化 MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 状态变量
        self.status = "Normal" 
        self.neck_inclination = 0 # [新增] 初始化角度变量
        self.start_time = time.time()

    def __del__(self):
        self.video.release()

    def calculate_angle(self, a, b, c):
        """
        计算三个点之间的角度 (用于判断驼背)
        """
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
            return None

        # 转换颜色空间 BGR -> RGB
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # MediaPipe 处理
        results = self.pose.process(image_rgb)

        # 重新允许写入，准备绘制
        image.flags.writeable = True
        
        # 获取画面尺寸
        h, w, _ = image.shape

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # --- 核心算法逻辑区域 ---
            
            # 1. 获取关键点坐标
            l_ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y * h]
            l_shldr = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            
            # 2. 简单的驼背判定
            vertical_point = [l_shldr[0], l_shldr[1] + 100] 
            
            # [修改] 使用 self.neck_inclination 存储，以便 get_data 调用
            self.neck_inclination = self.calculate_angle(l_ear, l_shldr, vertical_point)

            # 3. 判定逻辑 (阈值可调整)
            if self.neck_inclination < 150: 
                self.status = "Warning: Slouching!"
                color = (0, 0, 255) # 红色
            else:
                self.status = "Normal"
                color = (0, 255, 0) # 绿色

            # 4. 在画面上绘制信息
            cv2.putText(image, self.status, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            cv2.putText(image, f"Neck Angle: {int(self.neck_inclination)}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            # 绘制骨骼连线
            self.mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        # 编码为 JPEG 格式传输给前端
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_data(self):
        """[新增] 返回给前端的数据接口"""
        return {
            "status": self.status,
            "angle": int(self.neck_inclination),
            "timestamp": time.strftime("%H:%M:%S")
        }