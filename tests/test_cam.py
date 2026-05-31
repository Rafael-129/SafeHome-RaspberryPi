import cv2

cam = cv2.VideoCapture(0)

ok, frame = cam.read()

print("Camara:", ok)

cam.release()