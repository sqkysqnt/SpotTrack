import cv2
import socket
import struct
import time
from aiymakerkit import vision
import models

# Multicast settings
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5004
TTL = 1
MAX_PACKET_SIZE = 65507
FPS = 15
FRAME_INTERVAL = 1 / FPS

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

detector = vision.Detector(models.FACE_DETECTION_MODEL)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', TTL))
multicast_address = (MULTICAST_GROUP, MULTICAST_PORT)

frame_count = 0
last_sent_time = time.time()
while True:
    success, frame = cap.read()
    if not success:
        print("Failed to capture frame")
        continue
    
    faces = detector.get_objects(frame, threshold=0.1)
    vision.draw_objects(frame, faces)
    
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode frame")
        continue

    current_time = time.time()
    if current_time - last_sent_time >= FRAME_INTERVAL:
        buffer = buffer.tobytes()
        total_length = len(buffer)
        
        # Split the buffer into smaller chunks
        for i in range(0, total_length, MAX_PACKET_SIZE):
            chunk = buffer[i:i + MAX_PACKET_SIZE]
            sock.sendto(chunk, multicast_address)
            
        frame_count += 1
        last_sent_time = current_time
        print(f"Sent frame {frame_count}")

cap.release()
sock.close()

