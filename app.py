from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
import cv2
import numpy as np
from aiymakerkit import vision
import models
import time

app = FastAPI()

detector = vision.Detector(models.FACE_DETECTION_MODEL)
cap = cv2.VideoCapture(0)
boundary_color = (0, 165, 255)  # Orange in BGR format

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global boundary_color
    while True:
        data = await websocket.receive_text()
        if data == "toggle_color":
            if boundary_color == (0, 165, 255):
                boundary_color = (0, 255, 0)  # Green in BGR format
            else:
                boundary_color = (0, 165, 255)  # Orange in BGR format
            await websocket.send_text(f"Color toggled to {boundary_color}")

def gen_frames():
    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            break
        else:
            frame_copy = frame.copy()
            faces = detector.get_objects(frame_copy, threshold=0.1)
            vision.draw_objects(frame, faces, color=boundary_color)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elapsed_time = time.time() - start_time
        sleep_time = max(0, (1/15) - elapsed_time)
        time.sleep(sleep_time)

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Face Detection</title>
        </head>
        <body>
            <h1>Face Detection Video Stream</h1>
            <button id="toggle-button" onclick="toggleColor()">Toggle Color</button>
            <img src="/video_feed" width="100%">
            <script>
                let ws = new WebSocket("ws://" + location.host + "/ws");
                function toggleColor() {
                    ws.send("toggle_color");
                }
                ws.onmessage = function(event) {
                    const button = document.getElementById("toggle-button");
                    if (button.innerText === "Toggle Color to Green") {
                        button.innerText = "Toggle Color to Orange";
                    } else {
                        button.innerText = "Toggle Color to Green";
                    }
                };
            </script>
        </body>
    </html>
    """

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

