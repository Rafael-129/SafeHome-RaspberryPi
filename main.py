import time
import logging
from datetime import date
from config import SCAN_INTERVAL, LOG_FILE, RESIDENTES
from core.camera import Camera
from core.recognizer import Recognizer
from core.api_client import ApiClient
from core.sync_visitantes import sincronizar_visitantes

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
    sincronizar_visitantes()
    recognizer.cargar_encodings()

    camera = Camera()
    if not camera.conectar():
        log.error("No se pudo conectar a la camara.")
        return

    log.info("Camara conectada. Escaneando...")

    ultimo_reconocido = None
    ultimo_tiempo = 0
    ultimo_purge_dia = date.today()
    COOLDOWN = 8

    try:
        while True:
            # Purga diaria de fotos vencidas (politica de retencion de datos)
            hoy = date.today()
            if hoy != ultimo_purge_dia:
                log.info("Ejecutando purga diaria de fotos de visitantes...")
                resultado = api.purgar_fotos_vencidas()
                if resultado:
                    log.info(
                        f"Purga: {resultado.get('visitantes')} fotos y "
                        f"{resultado.get('capturas')} capturas eliminadas."
                    )
                sincronizar_visitantes()
                recognizer.cargar_encodings()
                ultimo_purge_dia = hoy

            frame = camera.capturar_frame()
            if frame is None:
                log.warning("Frame no disponible. Reintentando...")
                time.sleep(1)
                continue

            persona = recognizer.reconocer(frame)
            ahora = time.time()

            if persona is None:
                time.sleep(SCAN_INTERVAL)
                continue

            tipo = persona.get("tipo")

            # ── DESCONOCIDO ──────────────────────────────────────────
            if tipo == "desconocido":
                if ultimo_reconocido == "desconocido" and (ahora - ultimo_tiempo) < COOLDOWN:
                    time.sleep(0.5)
                    continue
                log.warning("Rostro desconocido. Acceso DENEGADO.")
                scanner_resp = api.registrar_escaneo_desconocido(frame)
                idscanner = scanner_resp.get("idscanner") if scanner_resp else None
                api.registrar_historial(None, idscanner, "Denegado")
                ultimo_reconocido = "desconocido"
                ultimo_tiempo = ahora
                time.sleep(SCAN_INTERVAL)
                continue

            # ── VISITANTE ─────────────────────────────────────────────
            if tipo == "visitante":
                idvisitante = persona.get("idvisitante")
                clave = f"visitante_{idvisitante}"
                if ultimo_reconocido == clave and (ahora - ultimo_tiempo) < COOLDOWN:
                    time.sleep(0.5)
                    continue
                log.info(f"Visitante reconocido: idvisitante={idvisitante}")
                scanner_resp = api.registrar_escaneo_visitante(idvisitante, frame)
                if scanner_resp and scanner_resp.get("autorizado"):
                    idscanner = scanner_resp.get("idscanner")
                    api.registrar_historial(None, idscanner, "Permitido", idvisitante=idvisitante)
                    log.info(f"Acceso PERMITIDO: visitante {idvisitante}")
                else:
                    api.registrar_historial(None, None, "Denegado", idvisitante=idvisitante)
                    log.warning(f"Acceso DENEGADO: visitante {idvisitante}")
                ultimo_reconocido = clave
                ultimo_tiempo = ahora
                time.sleep(SCAN_INTERVAL)
                continue

            # ── RESIDENTE ─────────────────────────────────────────────
            if tipo == "residente":
                nombre = persona.get("nombre")
                if ultimo_reconocido == nombre and (ahora - ultimo_tiempo) < COOLDOWN:
                    time.sleep(0.5)
                    continue
                idusuario = RESIDENTES.get(nombre)
                if idusuario is None:
                    log.warning(f"{nombre} sin idusuario en config.")
                    time.sleep(SCAN_INTERVAL)
                    continue
                log.info(f"Residente reconocido: {nombre} (idusuario={idusuario})")
                scanner_resp = api.registrar_escaneo(idusuario, frame)
                if scanner_resp and scanner_resp.get("autorizado"):
                    idscanner = scanner_resp.get("idscanner")
                    api.registrar_historial(idusuario, idscanner, "Permitido")
                    log.info(f"Acceso PERMITIDO: {nombre}")
                else:
                    api.registrar_historial(idusuario, None, "Denegado")
                    log.warning(f"Acceso DENEGADO: {nombre}")
                ultimo_reconocido = nombre
                ultimo_tiempo = ahora
                time.sleep(SCAN_INTERVAL)
                continue

    except KeyboardInterrupt:
        log.info("Scanner detenido.")
    finally:
        camera.desconectar()


if __name__ == "__main__":
    main()