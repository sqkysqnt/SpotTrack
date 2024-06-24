from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from picamera2 import Picamera2
import cv2
import numpy as np
import logging

app = FastAPI()

# Initialize the cameras
camera1 = Picamera2(camera_num=0)
camera1.configure(camera1.create_video_configuration(main={"format": "RGB888", "size": (640, 480)}))
camera1.start()

camera2 = Picamera2(camera_num=1)
camera2.configure(camera2.create_video_configuration(main={"format": "RGB888", "size": (640, 480)}))
camera2.start()

# Set up logging
logging.basicConfig(level=logging.INFO)

def generate_frames():
    while True:
        frame1 = camera1.capture_array()
        frame2 = camera2.capture_array()
        
        # Concatenate the frames horizontally
        combined_frame = np.concatenate((frame1, frame2), axis=1)
        
        ret, buffer = cv2.imencode('.jpg', combined_frame)
        if not ret:
            logging.error("Failed to encode frame.")
            continue
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
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
