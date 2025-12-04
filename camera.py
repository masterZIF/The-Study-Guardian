import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque  # [新增] 引入队列用于平滑数据

class VideoCamera(object):
    def __init__(self):
        # 0 代表默认摄像头
        self.video = cv2.VideoCapture(0) 
        
        # 强制设置低分辨率以保证流畅度 (保留之前的优化)
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
        
        # [优化] 初始化历史角度队列 (取最近 5 帧平均值)
        self.angle_history = deque(maxlen=5)

    def __del__(self):
        self.video.release()

    def calculate_angle(self, a, b, c):
        """
        计算三个点之间的角度
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

        # 重新允许写入
        image.flags.writeable = True
        h, w, _ = image.shape

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # 1. 获取坐标
            l_ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y * h]
            l_shldr = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            
            # 2. 计算当前帧的角度
            vertical_point = [l_shldr[0], l_shldr[1] + 100] 
            raw_angle = self.calculate_angle(l_ear, l_shldr, vertical_point)
            
            # [优化] 数据平滑：加入队列并计算平均值
            self.angle_history.append(raw_angle)
            avg_angle = sum(self.angle_history) / len(self.angle_history)
            self.neck_inclination = avg_angle # 更新为平滑后的值

            # [优化] 滞后比较 (防抖动)：设置 10 度的缓冲带
            # 只有当角度明显小于 145 才报警
            if avg_angle < 145: 
                self.status = "Warning: Slouching!"
            # 只有当角度明显回到 155 以上才恢复正常
            elif avg_angle > 155:
                self.status = "Normal"
            
            # (如果角度在 145-155 之间，保持上一帧的状态不变，避免闪烁)

            # [优化] 自定义骨骼样式：改为白色/淡色，配合可爱风
            landmark_spec = self.mp_drawing.DrawingSpec(
                color=(255, 255, 255), thickness=2, circle_radius=2
            )
            connection_spec = self.mp_drawing.DrawingSpec(
                color=(200, 255, 200), thickness=2, circle_radius=1
            )

            # 绘制骨骼
            self.mp_drawing.draw_landmarks(
                image, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=landmark_spec,
                connection_drawing_spec=connection_spec
            )

        # 编码为 JPEG
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_data(self):
        """返回给前端的数据接口"""
        return {
            "status": self.status,
            "angle": int(self.neck_inclination),
            "timestamp": time.strftime("%H:%M:%S")
        }