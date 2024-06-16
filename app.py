from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
import cv2
from aiymakerkit import vision, utils
import models
from pytube import YouTube
import shutil
import os

app = FastAPI()

# Object detection setup
detector = vision.Detector(models.OBJECT_DETECTION_MODEL)
labels = utils.read_labels_from_metadata(models.OBJECT_DETECTION_MODEL)

# Color toggle for bounding boxes
box_color = (0, 165, 255)  # Orange
cap = None
video_url = None
video_file_path = None
source_type = "camera"  # Default source

@app.on_event("shutdown")
def shutdown_event():
    global cap
    if cap:
        cap.release()

def gen_frames():
    global cap, box_color
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        else:
            frame_copy = frame.copy()  # Make a copy for detection
            objects = detector.get_objects(frame_copy, threshold=0.4)
            vision.draw_objects(frame, objects, labels, color=box_color)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Object Detection</title>
        </head>
        <body>
            <h1>Object Detection Video Stream</h1>
            <form id="sourceForm" action="/select_source" method="post" enctype="multipart/form-data">
                <label for="source">Select Source:</label>
                <select name="source" id="source">
                    <option value="camera">Camera</option>
                    <option value="file">File</option>
                    <option value="youtube">YouTube</option>
                </select>
                <br><br>
                <div id="fileInput" style="display:none;">
                    <input type="file" name="file" id="file">
                </div>
                <div id="youtubeInput" style="display:none;">
                    <input type="text" name="youtube_url" id="youtube_url" placeholder="Enter YouTube URL">
                </div>
                <button type="submit">Select</button>
            </form>
            <br>
            <img id="cameraFeed" src="/video_feed" width="100%">
            <br><br>
            <button onclick="toggleColor()">Toggle Box Color</button>
            <br><br>
            <input type="range" min="0" max="100" value="0" id="videoScrubber" style="width: 100%;" oninput="scrubVideo(this.value)">
            <script>
                document.getElementById('source').addEventListener('change', function() {
                    const fileInput = document.getElementById('fileInput');
                    const youtubeInput = document.getElementById('youtubeInput');
                    if (this.value === 'file') {
                        fileInput.style.display = 'block';
                        youtubeInput.style.display = 'none';
                    } else if (this.value === 'youtube') {
                        fileInput.style.display = 'none';
                        youtubeInput.style.display = 'block';
                    } else {
                        fileInput.style.display = 'none';
                        youtubeInput.style.display = 'none';
                    }
                });

                document.getElementById('sourceForm').addEventListener('submit', async function(event) {
                    event.preventDefault();
                    const formData = new FormData(this);
                    await fetch('/select_source', {
                        method: 'POST',
                        body: formData
                    });
                    document.getElementById('cameraFeed').src = '/video_feed';
                });

                function toggleColor() {
                    fetch('/toggle_color', { method: 'POST' });
                }

                function scrubVideo(value) {
                    fetch(`/scrub_video?position=${value}`, { method: 'POST' });
                }
            </script>
        </body>
    </html>
    """

@app.post("/select_source")
async def select_source(source: str = Form(...), file: UploadFile = File(None), youtube_url: str = Form(None)):
    global video_file_path, video_url, cap, source_type
    source_type = source
    if source == "camera":
        if cap:
            cap.release()
        cap = cv2.VideoCapture(0)
    elif source == "file" and file:
        video_file_path = f"uploaded_{file.filename}"
        with open(video_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if cap:
            cap.release()
        cap = cv2.VideoCapture(video_file_path)
    elif source == "youtube" and youtube_url:
        video_url = youtube_url
        if cap:
            cap.release()
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4').first()
        cap = cv2.VideoCapture(stream.url)
    return {"message": f"{source.capitalize()} selected"}

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/toggle_color")
async def toggle_color():
    global box_color
    if box_color == (0, 165, 255):  # Orange
        box_color = (0, 255, 0)  # Green
    else:
        box_color = (0, 165, 255)  # Orange
    return {"message": "Color toggled"}

@app.post("/scrub_video")
async def scrub_video(position: int):
    global cap, source_type
    if source_type in ["file", "youtube"]:
        if cap:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            target_frame = int((position / 100) * total_frames)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    return {"message": "Scrubbed to position"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

