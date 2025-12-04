from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera

app = Flask(__name__)

# 全局单例模式：确保视频流和状态查询使用的是同一个摄像头实例
video_camera = None

def get_camera():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    return video_camera

def gen(camera):
    """视频流生成器"""
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(get_camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status_feed():
    """前端 JS 会每隔几毫秒请求这个接口获取最新状态"""
    camera = get_camera()
    return jsonify(camera.get_data())

if __name__ == '__main__':
    # 端口改为 5001 避开冲突
    app.run(host='0.0.0.0', port=5001, debug=True)