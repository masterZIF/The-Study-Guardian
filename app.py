from flask import Flask, render_template, Response
from camera import VideoCamera

app = Flask(__name__)

def gen(camera):
    """视频流生成器函数"""
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # debug=True 方便调试，代码改动后自动重启
    app.run(host='0.0.0.0', port=5001, debug=True)