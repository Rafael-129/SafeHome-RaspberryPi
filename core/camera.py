import threading
import time
import cv2
import requests
import numpy as np
from config import CAMERA_URL, CAMERA_STREAM_URL


class Camera:
    def __init__(self):
        self.url_jpg = CAMERA_URL
        self.url_stream = CAMERA_STREAM_URL
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

    def conectar(self):
        # Intentar abrir el stream MJPEG (conexion persistente, sin lag).
        self.cap = cv2.VideoCapture(self.url_stream)
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        if not self.cap.isOpened():
            # Fallback: modo HTTP shot.jpg.
            self.cap.release()
            self.cap = None
            return self._verificar_http()

        self.running = True
        self.thread = threading.Thread(target=self._actualizar, daemon=True)
        self.thread.start()

        # Esperar a recibir el primer frame (hasta ~5s).
        for _ in range(50):
            with self.lock:
                if self.frame is not None:
                    return True
            time.sleep(0.1)

        # El stream abrio pero no entrega frames: caer al modo HTTP.
        self.desconectar()
        return self._verificar_http()

    def _actualizar(self):
        while self.running and self.cap is not None:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            with self.lock:
                self.frame = frame

    def capturar_frame(self):
        if self.cap is not None:
            with self.lock:
                return None if self.frame is None else self.frame.copy()
        return self._capturar_http()

    def _capturar_http(self):
        try:
            resp = requests.get(self.url_jpg, timeout=5)
            if resp.status_code != 200:
                return None
            img_array = np.frombuffer(resp.content, dtype=np.uint8)
            return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception:
            return None

    def _verificar_http(self):
        try:
            resp = requests.get(self.url_jpg, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def desconectar(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
            self.thread = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None
