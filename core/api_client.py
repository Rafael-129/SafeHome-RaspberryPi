import base64
import json
import logging
from datetime import datetime
import cv2
import requests
from config import API_BASE_URL

log = logging.getLogger("SafeHome")


class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def verificar_conexion(self):
        try:
            resp = self.session.get(f"{API_BASE_URL}/health/", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def frame_a_base64(self, frame):
        pequeno = cv2.resize(frame, (400, 300))
        _, buffer = cv2.imencode(".jpg", pequeno, [cv2.IMWRITE_JPEG_QUALITY, 70])
        return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

    def registrar_escaneo(self, idusuario, frame):
        foto = self.frame_a_base64(frame)
        payload = {
            "idusuario": idusuario,
            "idvisitante": None,
            "foto_capturada": foto,
            "tipo_persona": "residente",
        }
        try:
            resp = self.session.post(f"{API_BASE_URL}/scanner/", data=json.dumps(payload), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.error(f"Error en scanner: {e}")
            log.error(f"Respuesta completa: {e.response.text if e.response is not None else 'Sin respuesta'}")
            return None
            
    def registrar_escaneo_visitante(self, idvisitante, frame):
        foto = self.frame_a_base64(frame)
        payload = {
            "idusuario": None,
            "idvisitante": idvisitante,
            "foto_capturada": foto,
            "tipo_persona": "visitante",
        }
        try:
            resp = self.session.post(f"{API_BASE_URL}/scanner/", data=json.dumps(payload), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.error(f"Error en scanner visitante: {e}")
            return None

    def registrar_escaneo_desconocido(self, frame):
        foto = self.frame_a_base64(frame)
        payload = {
            "idusuario": None,
            "idvisitante": None,
            "foto_capturada": foto,
            "tipo_persona": "desconocido",
        }
        try:
            resp = self.session.post(f"{API_BASE_URL}/scanner/", data=json.dumps(payload), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.error(f"Error en scanner desconocido: {e}")
            return None

    def registrar_historial(self, idusuario, idscanner, estado, idvisitante=None):
        ahora = datetime.now()
        payload = {
            "idusuario": idusuario,
            "idvisitante": idvisitante,
            "idscanner": idscanner,
            "fecha_entrada": ahora.strftime("%Y-%m-%d"),
            "hora_entrada": ahora.strftime("%H:%M:%S"),
            "hora_salida": None,
            "estado": estado,
        }
        try:
            resp = self.session.post(f"{API_BASE_URL}/historial/", data=json.dumps(payload), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            log.error(f"Error en historial: {e}")
            return None