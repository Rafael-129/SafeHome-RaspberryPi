import cv2

url = "http://192.168.1.14:8080/video"

cap = cv2.VideoCapture(url)

ret, frame = cap.read()

print("Conectado:", ret)

if ret:
    print("Resolucion:", frame.shape)

cap.release()

