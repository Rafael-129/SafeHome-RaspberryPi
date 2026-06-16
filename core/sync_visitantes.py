import base64
import io
import os
import pickle
import requests
import face_recognition
import numpy as np
from PIL import Image
from config import API_BASE_URL, ENCODINGS_DIR


def foto_a_encoding(foto_b64):
    try:
        if "," in foto_b64:
            foto_b64 = foto_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(foto_b64)
        img_pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img_pil)
        encodings = face_recognition.face_encodings(img_np)
        if encodings:
            return encodings[0]
    except Exception as e:
        print(f"Error decodificando foto: {e}")
    return None


def sincronizar_visitantes():
    print("Sincronizando visitantes...")
    try:
        resp = requests.get(f"{API_BASE_URL}/visitantes/", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        visitantes = data.get("results", data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error al obtener visitantes: {e}")
        return

    ids_validos = {v.get("idvisitante") for v in visitantes}

    for archivo in os.listdir(ENCODINGS_DIR):
        if not archivo.startswith("visitante_") or not archivo.endswith("_encoding.pkl"):
            continue
        idvisitante = int(archivo.replace("visitante_", "").replace("_encoding.pkl", ""))
        if idvisitante not in ids_validos:
            os.remove(os.path.join(ENCODINGS_DIR, archivo))
            print(f"  Encoding eliminado (visitante {idvisitante} ya no existe): {archivo}")

    nuevos = 0
    for v in visitantes:
        idvisitante = v.get("idvisitante")
        foto = v.get("foto")

        if not idvisitante:
            continue

        ruta_pkl = os.path.join(ENCODINGS_DIR, f"visitante_{idvisitante}_encoding.pkl")

        # Foto purgada (retencion 30 dias): el visitante existe pero ya no tiene
        # foto, asi que eliminamos su encoding para que deje de reconocerse.
        if not foto:
            if os.path.exists(ruta_pkl):
                os.remove(ruta_pkl)
                print(f"  Encoding eliminado (foto purgada): visitante_{idvisitante}")
            continue

        if os.path.exists(ruta_pkl):
            continue

        encoding = foto_a_encoding(foto)
        if encoding is None:
            print(f"  Sin rostro en foto de visitante {idvisitante}")
            continue

        with open(ruta_pkl, "wb") as f:
            pickle.dump(encoding, f)

        print(f"  Encoding guardado: visitante_{idvisitante}")
        nuevos += 1

    print(f"Sincronización completa: {nuevos} visitantes nuevos procesados.")