import sys
import os

# Add the virtual environment's site-packages to sys.path
venv_path = "/home/jeremy/venv/lib/python3.11/site-packages"
sys.path.append(venv_path)

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

# Initialize Hailo
hef_path = "/usr/share/hailo-models/yolov6n.hef"
device = hailo.Device()
hef = hailo.Hef(hef_path)
network_group = device.configure(hef)
network_group_params = network_group.create_params()
input_vstream = network_group.get_input_vstream()
output_vstream = network_group.get_output_vstream()
input_vstream.activate()
output_vstream.activate()

def run_inference_on_frame(frame):
    # Preprocess frame if necessary (e.g., resizing, normalization)
    preprocessed_frame = cv2.resize(frame, (640, 480))
    preprocessed_frame = preprocessed_frame.astype(np.uint8)

    # Run inference
    input_vstream.write(preprocessed_frame)
    output = output_vstream.read()

    # Post-process output to extract bounding boxes and other information
    results = []  # Replace with actual parsing of 'output'
    return results

def draw_bounding_boxes(frame, results):
    for result in results:
        x, y, w, h = result['bbox']
        confidence = result['confidence']
        class_id = result['class_id']
        label = f"Class {class_id}: {confidence:.2f}"

        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def generate_frames():
    while True:
        frame1 = camera1.capture_array()
        frame2 = camera2.capture_array()
        
        # Concatenate the frames horizontally
        combined
