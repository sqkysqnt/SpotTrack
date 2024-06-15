from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import cv2
import base64
import threading
import time

app = FastAPI()

# Initialize camera and face detector
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Error: Could not open video device.")

detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
clients = []

def capture_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        for client in clients:
            try:
                client.send_text(frame_data)
            except WebSocketDisconnect:
                clients.remove(client)
        time.sleep(1 / 15)  # Limit to 15 FPS

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Video Feed</title>
        </head>
        <body>
            <h1>Video Feed</h1>
            <img id="video" width="100%">
            <script>
                let socket = new WebSocket("ws://" + window.location.host + "/ws");
                socket.onmessage = function(event) {
                    let image = document.getElementById('video');
                    image.src = 'data:image/jpeg;base64,' + event.data;
                };
            </script>
        </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=capture_frames, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

