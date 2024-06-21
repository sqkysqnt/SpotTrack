import cv2

# Open the video capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Frame', frame)
        print("Press any key to close the window")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error: Could not read frame")
    
    cap.release()
