from PIL import Image
import cv2
import numpy as np
from src.model_images import cv2_to_pil
import pytesseract

CONFIDENCE_THRESHOLD = 0.8

tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract'
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract'
TESSDATA_PREFIX= 'C:\\Program Files\\Tesseract-OCR'
tessdata_dir_config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

net = cv2.dnn.readNet("qrcode-yolov3-tiny_last.weights", "qrcode-yolov3-tiny.cfg")

classes = []
with open("qrcode.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def get_data(image):
    img = image.copy()
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    text = pytesseract.image_to_string(img, config=tessdata_dir_config)
    text = text.split('\n')

    for i in text:
        if (i=='') or (i==' ') or (i=='  ') or (i=='.') or (i==','):
            text.remove(i)

    data = {}
    for i, phrase in enumerate(text):
        if 'Permanent Account Number Card' in phrase:
            data['PAN_No'] = text[i+1]
        if "Father's Name" in phrase:
            data['Name'] = text[i-1]
            data['Father_Name'] = text[i+1]
        if 'Signature' in phrase:
            issue_date = str(text[i+2])
            data['Issue_Date'] = str(issue_date[:2] + '/' + issue_date[2:4] + '/' + issue_date[4:])
        if 'Date of Birth' in phrase:
            data['DOB'] = text[i+1][:11]

    return data

def get_face(image):    
    face_img = image.copy()   
    face_rect = face_cascade.detectMultiScale(face_img, scaleFactor = 1.2, minNeighbors = 5) 
    for (x, y, w, h) in face_rect: 
        cv2.rectangle(face_img, (x, y), (x + w, y + h), (255, 255, 255), 10)

    face_img = face_img[y:y+h, x:x+w] 
    return face_img 

def get_qr(image):

    img = image[:, :]
    height, width, channels = img.shape 
    h32 = 32*(height//32)
    w32 = 32*(width//32)


    blob = cv2.dnn.blobFromImage(img, 1/255, (h32, w32), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > CONFIDENCE_THRESHOLD:
                
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    qr_code = None
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            qr_code = img[y:y+h, x:x+w]
    
    return qr_code
    

def scan_aadhar(img_path):

    image = cv2.imread(img_path)
    
    data = get_data(image)
    
    face_img = get_face(image)
    filename = 'pan_face.jpeg'
    cv2.imwrite(filename, face_img)

    qr_code = get_qr(image) 
    qr_filename = 'pan_qr_code.jpeg'
    cv2.imwrite(qr_filename, qr_code)

    return data, face_img, qr_code

data, face_img, qr_code = scan_aadhar('pan.jpeg')

def display_data(data, face_img, qr_code):
    for key in data:
        print(key, ' '*(15-len(key)),':    ', data[key])
    face_img = cv2_to_pil(face_img)
    qr_code = cv2_to_pil(qr_code)
    face_img.show()
    qr_code.show()

display_data(data, face_img, qr_code)