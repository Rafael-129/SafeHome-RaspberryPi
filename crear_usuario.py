import requests
from datetime import datetime

ahora = datetime.now()

payload = {
    "idusuario": 4,
    "idvisitante": None,
    "idscanner": None,
    "fecha_entrada": ahora.strftime("%Y-%m-%d"),
    "hora_entrada": ahora.strftime("%H:%M:%S"),
    "hora_salida": None,
    "estado": "Permitido"
}

resp = requests.post(
    'https://backendservice-d2bkaahtawavhkb0.canadacentral-01.azurewebsites.net/api/historial/',
    json=payload,
    timeout=30
)

print("Status:", resp.status_code)
print("Respuesta:", resp.text[:500])