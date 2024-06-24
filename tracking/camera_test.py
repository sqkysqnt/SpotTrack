from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import uvicorn

app = FastAPI()

# Initialize the camera
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/')
async def main_page():
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Video Streaming</title>
        </head>
        <body>
            <h1>Video Streaming</h1>
            <img src="/video_feed">
        </body>
    </html>
    """, status_code=200)

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
