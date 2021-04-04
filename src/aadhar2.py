from PIL import Image
import cv2
import numpy as np
from model_images import cv2_to_pil


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def save_face1(img_path):
    image = cv2.imread(img_path)

    face_img = image.copy()
    face_rect = face_cascade.detectMultiScale(face_img, scaleFactor = 1.2, minNeighbors = 5)
    for (x, y, w, h) in face_rect:

        face_img = face_img[y:y+h, x:x+w]
    filename = 'E:\kyc-auth-master\src\images/a.jpeg'
    cv2.imwrite(filename, face_img)
