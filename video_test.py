from fastapi import FastAPI, Response
from starlette.responses import StreamingResponse
import cv2

app = FastAPI()

def gen_frames():
    # Try to open each video device until one works
    for i in range(17):  # Update range if you have more than 16 devices
        print("Trying /dev/video{}".format(i))  # Debug print
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print("Opened video device /dev/video{}".format(i))
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    print("Failed to read frame from /dev/video{}".format(i))  # Debug print
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            cap.release()
            break
        else:
            print("Cannot open /dev/video{}".format(i))  # Debug print
            cap.release()
    else:
        print("Cannot open any video device")

@app.get("/")
def read_root():
    return {"message": "Welcome to SpotTrack"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

