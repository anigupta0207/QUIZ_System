import cv2
import numpy as np
import os 
import time 
from collections import deque
import signal
import sys
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
suspect_file = os.path.abspath(os.path.join(BASE_DIR, "..", "suspect_count.json"))

if not os.path.exists(suspect_file):
    with open(suspect_file, "w") as f:
        json.dump({"current": 0}, f)

def add_suspect():
    data = json.load(open(suspect_file))
    data["current"] += 1
    json.dump(data, open(suspect_file, "w"))

# ✅ Save suspicious event photo (no CSV)
def capture_suspicious_event(event_type, frame):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'captures/{event_type}_{timestamp}.jpg'
    cv2.imwrite(filename, frame)
    print(f"📸 Suspicious event captured: {event_type} -> {filename}")


# ✅ Shutdown handler
stop_signal = False
def handle_exit(signum, frame):
    global stop_signal
    stop_signal = True

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

os.makedirs('captures', exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

prev_face_position = None
movement_threshold = 10
movement_history = deque(maxlen=3)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

capture_interval = 5
last_capture_time = time.time()

# ✅ Exit loop when SIGTERM is received
while not stop_signal:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ ALERT: Failed to grab frame!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(60, 60),
        maxSize=(400, 400)
    )

    if len(faces) > 0:

        # ✅ MULTIPLE FACES FOUND
        if len(faces) > 1:
            cv2.putText(frame, "⚠ MULTIPLE FACES DETECTED!", (50, 100),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            print("⚠ MULTIPLE FACES DETECTED!")
            
            capture_suspicious_event("multiface", frame)
            add_suspect()
            
        # ✅ Select largest face for tracking
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        (x, y, w, h) = largest_face
        center_current = (x + w//2, y + h//2)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # ✅ Detect face movement
        if prev_face_position is not None:
            dx = abs(center_current[0] - prev_face_position[0])
            dy = abs(center_current[1] - prev_face_position[1])
            distance = np.sqrt(dx**2 + dy**2)

            if distance > movement_threshold:
                cv2.putText(frame, "⚠ FACE MOVEMENT!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                print("⚠ FACE MOVEMENT DETECTED!")

                capture_suspicious_event("movement", frame)
                add_suspect()
                
        prev_face_position = center_current

    else:
        prev_face_position = None
        cv2.putText(frame, "No face detected!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
    cv2.imshow("Face Monitoring", frame)
    key = cv2.waitKey(1)
    if key == ord('q') or key == ord('Q'):
        print("👋 Face monitoring stopped manually (Q pressed).")
        break
cap.release()
cv2.destroyAllWindows()
