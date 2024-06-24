from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import subprocess
import logging
import os

app = FastAPI()

json_config_path = "/home/jeremy/SpotTrack/tracking/hailo_yolov6_inference.json"
output_file_path = "/home/jeremy/SpotTrack/tracking/output.h264"

logging.basicConfig(level=logging.INFO)

def run_rpicam_vid():
    command = [
        "rpicam-vid",
        "-t", "0",
        "--post-process-file", json_config_path,
        "--lores-width", "640",
        "--lores-height", "480",  # Adjusting resolution to avoid errors
        "-o", output_file_path  # Output to file
    ]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def generate_frames():
    with open(output_file_path, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

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
    run_rpicam_vid()
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
