from picamera2 import Picamera2
import time

def capture_image():
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    picam2.start()
    time.sleep(2)  # Give the camera some time to adjust settings
    picam2.capture_file("test_picamera2.jpg")
    picam2.stop()

if __name__ == "__main__":
    capture_image()
