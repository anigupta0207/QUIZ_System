import cv2
import numpy as np
import os 
import time 

#face detetion and movement part and 5 sec 

os.makedirs('captures',exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

prev_face_position = None
movement_threshold = 16

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 500)

# 5 second timer for photo capture
capture_interval = 5  # seconds
last_capture_time = time.time()


while True:
    ret, frame = cap.read()
    if not ret:
        print("ALERT: Failed to grab frame!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.09, minNeighbors=5)

    if len(faces) == 1:
        (x, y, w, h) = faces[0]
        center_current = (x + w // 2, y + h // 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # draw rectangle around face

        if prev_face_position is not None:
            dx = abs(center_current[0] - prev_face_position[0])
            dy = abs(center_current[1] - prev_face_position[1])
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > movement_threshold:
                cv2.putText(frame, "Face Movement Detected! ALERT!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                print("Face movement detected! Distance moved:", distance)

        prev_face_position = center_current

    elif len(faces) == 0:
        prev_face_position = None
        cv2.putText(frame, "No face detected!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
    else:
        prev_face_position = None
        cv2.putText(frame, "Multiple faces detected!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        print("🚨 Multiple faces detected!")
    
    #5 secound photo capture storing 
    current_time=time.time()
    if current_time - last_capture_time >= capture_interval:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'captures/photo_{timestamp}.jpg'
        cv2.imwrite(filename, frame)
        print(f"📸 Photo captured and saved as {filename}")
        last_capture_time = current_time

    cv2.imshow("Face checking", frame)

    if cv2.waitKey(1)==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
