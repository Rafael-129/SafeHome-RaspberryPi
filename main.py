import time
import logging
from config import SCAN_INTERVAL, LOG_FILE, RESIDENTES
from core.camera import Camera
from core.recognizer import Recognizer
from core.api_client import ApiClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE),
    ],
)
log = logging.getLogger("SafeHome")


def main():
    log.info("Iniciando SafeHome Scanner...")

    api = ApiClient()
    if not api.verificar_conexion():
        log.error("No se pudo conectar al backend. Verifica internet.")
        return

    log.info("Backend conectado.")

    recognizer = Recognizer()
    recognizer.cargar_encodings()

    camera = Camera()
    if not camera.conectar():
        log.error("No se pudo conectar a la camara.")
        return

    log.info("Camara conectada. Escaneando...")

    ultimo_reconocido = None
    ultimo_tiempo = 0
    COOLDOWN = 8

    try:
        while True:
            frame = camera.capturar_frame()
            if frame is None:
                log.warning("Frame no disponible. Reintentando...")
                time.sleep(1)
                continue

            nombre = recognizer.reconocer(frame)

            if nombre is None:
                time.sleep(SCAN_INTERVAL)
                continue

            if nombre == "desconocido":
                ahora = time.time()
                if ultimo_reconocido == "desconocido" and (ahora - ultimo_tiempo) < COOLDOWN:
                    time.sleep(0.5)
                    continue
                log.warning("Rostro desconocido detectado. Acceso DENEGADO.")
                scanner_resp = api.registrar_escaneo(None, frame)
                if scanner_resp:
                    idscanner = scanner_resp.get("idscanner")
                    api.registrar_historial(None, idscanner, "Denegado", idvisitante=8)
                ultimo_reconocido = "desconocido"
                ultimo_tiempo = ahora
                time.sleep(SCAN_INTERVAL)
                continue

            # Residente reconocido
            ahora = time.time()
            if nombre == ultimo_reconocido and (ahora - ultimo_tiempo) < COOLDOWN:
                time.sleep(0.5)
                continue

            idusuario = RESIDENTES.get(nombre)
            if idusuario is None:
                log.warning(f"{nombre} reconocido pero sin idusuario en config.")
                time.sleep(SCAN_INTERVAL)
                continue

            log.info(f"Reconocido: {nombre} (idusuario={idusuario})")
            scanner_resp = api.registrar_escaneo(idusuario, frame)

            if scanner_resp and scanner_resp.get("autorizado"):
                idscanner = scanner_resp.get("idscanner")
                api.registrar_historial(idusuario, idscanner, "Permitido")
                log.info(f"Acceso PERMITIDO: {nombre}")
            else:
                log.warning(f"Acceso DENEGADO: {nombre}")

            ultimo_reconocido = nombre
            ultimo_tiempo = ahora

            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        log.info("Scanner detenido.")
    finally:
        camera.desconectar()


if __name__ == "__main__":
    main()