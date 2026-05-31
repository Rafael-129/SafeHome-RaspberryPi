import face_recognition
import pickle

imagen = face_recognition.load_image_file("rafael.jpg")

encodings = face_recognition.face_encodings(imagen)

if len(encodings) == 0:
    print("No se detectó ningún rostro")
    exit()

encoding = encodings[0]

with open("rafael_encoding.pkl", "wb") as f:
    pickle.dump(encoding, f)

print("Encoding guardado")