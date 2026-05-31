import cv2
import face_recognition
import pickle

url = "http://192.168.1.14:8080/video"

with open("rafael_encoding.pkl", "rb") as f:
    encoding_conocido = pickle.load(f)

cap = cv2.VideoCapture(url)

ret, frame = cap.read()

if not ret:
    print("No se pudo leer la camara")
    exit()

rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

encodings = face_recognition.face_encodings(rgb)

if len(encodings) == 0:
    print("No se encontró rostro")
else:
    resultado = face_recognition.compare_faces(
        [encoding_conocido],
        encodings[0],
        tolerance=0.6
    )

    if resultado[0]:
        print("Sandra reconocida")
    else:
        print("Desconocido")

cap.release()