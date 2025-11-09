import cv2
import numpy as np
import os 
import time 
from collections import deque

os.makedirs('captures', exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

prev_face_position = None
movement_threshold = 10  # Slightly lower for better sensitivity
movement_history = deque(maxlen=3)  # Keep track of recent movements

# Initialize camera with better resolution
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Higher resolution for better detection
cap.set(4, 720)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus

# Photo capture settings
capture_interval = 5  # seconds
last_capture_time = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ ALERT: Failed to grab frame!")
        break

    # Improve image quality for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray) 
    
    # More accurate face detection parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,    # Lower scale factor for better accuracy
        minNeighbors=6,     # More neighbors for reliable detection
        minSize=(60, 60),   # Minimum face size
        maxSize=(400, 400)  # Maximum face size
    )

    if len(faces) > 0:  # Process the largest face even if multiple faces are detected
        # Get the largest face (assuming it's the closest/main face)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        (x, y, w, h) = largest_face
        center_current = (x + w // 2, y + h // 2)
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Movement detection
        if prev_face_position is not None:
            dx = abs(center_current[0] - prev_face_position[0])
            dy = abs(center_current[1] - prev_face_position[1])
            distance = np.sqrt(dx**2 + dy**2)
            
            if distance > movement_threshold:
                cv2.putText(frame, "⚠️ ALERT: Face Movement!", (50, 50),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                print("⚠️ Face movement detected!")
        
        prev_face_position = center_current
    else:
        prev_face_position = None
        cv2.putText(frame, "No face detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
    
    # 5 second photo capture with validation
    current_time = time.time()
    if current_time - last_capture_time >= capture_interval:
        # Only capture if face is clearly visible
        if len(faces) == 1:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'captures/photo_{timestamp}.jpg'
            cv2.imwrite(filename, frame)
            print(f"📸 Photo captured and saved as {filename}")
        else:
            print("⚠️ Photo skipped - No clear face detected")
        last_capture_time = current_time

    # Removed movement level indicator to simplify the display

    cv2.imshow("Face Movement Detection", frame)

    if cv2.waitKey(1) == ord('q'):
        print("👋 Stopping detection...")
        break

cap.release()
cv2.destroyAllWindows()