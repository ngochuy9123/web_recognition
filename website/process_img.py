from flask import Blueprint, request, jsonify
import os
import cv2
import pickle
import numpy as np
# import face_recognition
from io import BytesIO
from PIL import Image
import base64
from .extensions import mysql
import insightface
from insightface.app import FaceAnalysis
import pandas as pd
from sklearn.metrics import pairwise
from .faceProcess import getImages,ml_search_algorithm,app_sc,dataframe

process_img = Blueprint('process_img',__name__)

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
        
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        userid,status = face_recog_by_insightface(img)
        _, img_encoded = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        if userid == 0:
            response = {
            "image": "None",
            "username":"Unknown",
            "email":"Unknown",
            "phone":"Unknown",
            "status":status
        }
        else:
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * FROM account where id = {userid}")
            data = cur.fetchall()
            cur.close()
            print(f"UserName: {data[0][1]}")
            username = data[0][1]
            email = data[0][2]
            phone = data[0][3]
            response = {
            "image": img_base64,
            "username":username,
            "email":email,
            "phone":phone,
            "status":status
        }
        return jsonify(response)

    return "Failed to get image", 500

def getIdFromName(name):
    return name.split("_")[0]
def img_process(img):
    down_points = (640, 512)
    img = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
    h,w,c = img.shape
    return img




def face_recog_by_insightface(img):
    userid = 0
    status = 0
    img = img_process(img)
    results_sc = app_sc.get(img)
    img_copy = img.copy()
    for res in results_sc:
        x1,y1,x2,y2 = res['bbox'].astype(int)
        emmbeddings = res['embedding']
        person_name = ml_search_algorithm(dataframe, "Facial_Features", test_vector=emmbeddings, name=["Name"],thresh=0.5)
        if str(person_name) == "Unknown":
            userid = 0
        else:
            userid = int(person_name)
            status = 1

    return userid,status





# def face_recog_by_lib(img):
#     faceCurFrame = face_recognition.face_locations(img)
#     encodeCurFrame = face_recognition.face_encodings(img, faceCurFrame)
#     print(len(faceCurFrame))
#     face_info = []
#     status = 0
#     response = {}
#     name = "Unknown"
#     for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        
#         matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
#         faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
#         matchIndex = np.argmin(faceDis)
        
#         if matches[matchIndex]:
#             name = personIds[matchIndex]

#             id = getIdFromName(name)
#             cur = mysql.connection.cursor()
#             query = "SELECT * FROM account WHERE id = %s"
#             cur.execute(query, (id,))
#             data = cur.fetchall()
#             print(data)
#             cur.close()

#             face_info.append(name)
#             status=1
#         else:
#             status = 0

#     return name,status

