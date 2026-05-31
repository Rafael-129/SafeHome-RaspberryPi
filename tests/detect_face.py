import cv2
import face_recognition

url = "http://192.168.1.14:8080/video"

cap = cv2.VideoCapture(url)

ret, frame = cap.read()

if not ret:
    print("No se pudo leer la camara")
    exit()

rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

faces = face_recognition.face_locations(rgb)

print("Rostros encontrados:", len(faces))

cap.release()