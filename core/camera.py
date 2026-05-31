import cv2
import requests
import numpy as np
from config import CAMERA_URL


class Camera:
    def __init__(self):
        self.url_jpg = CAMERA_URL

    def conectar(self):
        try:
            resp = requests.get(self.url_jpg, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def capturar_frame(self):
        try:
            resp = requests.get(self.url_jpg, timeout=5)
            if resp.status_code != 200:
                return None
            img_array = np.frombuffer(resp.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return frame
        except Exception:
            return None

    def desconectar(self):
        pass