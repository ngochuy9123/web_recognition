from flask import Blueprint, request, jsonify
import os
import cv2
import pickle
import numpy as np
import face_recognition
from io import BytesIO
from PIL import Image
import base64

process_img = Blueprint('process_img',__name__)
print("Loading Encode File ...")
file = open("website/EncodeFile.p","rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,personIds = encodeListKnownWithIds
print("Encode File Loaded")




@process_img.route('/processImg', methods=["POST"])
def save_img():
    if 'image' not in request.files:
        return "No image part", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        file_stream = BytesIO(file.read())
        img = np.array(Image.open(file_stream))
        # Process the image
        # imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(img.shape)
        # while True:
        #     cv2.imshow("Face Recognition",img)
        #     key = cv2.waitKey(1)
        #     if key == ord("q"):
        #         break
        name,status = face_recog_by_lib(img)
        _, img_encoded = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        
        response = {
            "image": img_base64,
            "name": name,
            "status":status
        }

        return jsonify(response)

    return "Failed to save image", 500


def face_recog_by_lib(img):
    faceCurFrame = face_recognition.face_locations(img)
    encodeCurFrame = face_recognition.face_encodings(img, faceCurFrame)
    print(len(faceCurFrame))
    face_info = []
    status = 0
    response = {}
    name = "Unknown"
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        matchIndex = np.argmin(faceDis)
        
        if matches[matchIndex]:
            name = personIds[matchIndex]
            print(name)
            face_info.append(name)
            status=1
            # y1, x2, y2, x1 = faceLoc
            # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            # cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # cv2.putText(img, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        else:
            
            status = 0

    return name,status

def face_recog_by_insightface(img):
    return "Test InsightFace"