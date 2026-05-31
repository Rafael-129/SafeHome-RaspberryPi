import os
import pickle
import face_recognition
import numpy as np
import cv2
from config import ENCODINGS_DIR, TOLERANCE


class Recognizer:
    def __init__(self):
        self.encodings = []
        self.nombres = []

    def cargar_encodings(self):
        self.encodings = []
        self.nombres = []

        for archivo in os.listdir(ENCODINGS_DIR):
            if archivo.endswith(".pkl"):
                ruta = os.path.join(ENCODINGS_DIR, archivo)
                with open(ruta, "rb") as f:
                    encoding = pickle.load(f)
                nombre = archivo.replace("_encoding.pkl", "")
                self.encodings.append(encoding)
                self.nombres.append(nombre)

        print(f"Encodings cargados: {len(self.encodings)}")

    def reconocer(self, frame):
        rgb = frame[:, :, ::-1].copy()
        small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
        ubicaciones = face_recognition.face_locations(small)

        if not ubicaciones:
            return None

        ubicaciones_full = [(t*2, r*2, b*2, l*2) for t, r, b, l in ubicaciones]
        encodings_frame = face_recognition.face_encodings(rgb, ubicaciones_full)

        if not encodings_frame:
            return None

        distancias = face_recognition.face_distance(self.encodings, encodings_frame[0])
        idx = int(np.argmin(distancias))

        if distancias[idx] <= TOLERANCE:
            return self.nombres[idx]

        return "desconocido"