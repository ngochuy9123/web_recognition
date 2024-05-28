from flask import Blueprint, request, jsonify,render_template
import os
import cv2
import pickle
import numpy as np
from io import BytesIO
from PIL import Image
import base64
from .extensions import mysql
import insightface
from insightface.app import FaceAnalysis
import pandas as pd
from sklearn.metrics import pairwise
import json

auth = Blueprint('auth',__name__)
folderModel = "indightface_models/"
app_sc = FaceAnalysis(name='buffalo_sc', 
                     root = "insightface_model",
                     providers=['CPUExecutionProvider'])
app_sc.prepare(ctx_id = 0, det_size=(640,640))

@auth.route('/login')
def login():
    return "<p>Login</p>"

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/signup')
def signup():
    return render_template("signup.html")

@auth.route('/signup', methods=["POST"])
def signup2():
    print("Insert start")
    username = request.form.get("username")
    email = request.form.get("email")
    phone = request.form.get("phone")
    print(f"Username: {username}, email: {email}, phone: {phone}")
    insertAccount(username,email,phone)
    response = {
        "status":True
    }
    return jsonify(response)
    

@auth.route('/signup1', methods=["POST"])
def signup1():
    if 'image' not in request.files:
        return "No image part", 400
    file = request.files['image']
    lstFaceDirection = json.loads(request.form.get("lstFaceDirection"))
    print(lstFaceDirection)
    # direction = int(request.form.get("faceDirection")) 
    if file.filename == '':
        return "No selected file", 400
    if file:
        file_stream = BytesIO(file.read())
        img = np.array(Image.open(file_stream))
        # Process the image
        # imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        faceDirection = -1
        idUser = getIdLastest()
        # isProcess = processImage(img,idUser,direction)
        faceDirection,status,message = detectDirectionFace(img,idUser,lstFaceDirection)
        if (status == True):
            lstFaceDirection.append(faceDirection)
            print(lstFaceDirection)
        response = {
            "faceDirection":faceDirection,
            "status":status,
            "lstFaceDirection":lstFaceDirection
        }
        return jsonify(response)
    return "Failed to save image", 500

def npAngle(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b) 
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

def calculate_pitch(landmarks):
    left_eye = landmarks[0]
    right_eye = landmarks[1]
    nose = landmarks[2]
    mouth_left = landmarks[3]
    mouth_right = landmarks[4]

    mid_eye = (left_eye + right_eye) / 2
    mid_mouth = (mouth_left + mouth_right) / 2

    # Vector từ mũi đến giữa hai mắt
    nose_to_mid_eye_vector = np.array(nose) - np.array(mid_eye)
    # Vector từ mũi đến giữa hai miệng
    nose_to_mid_mouth_vector = np.array(mid_mouth) - np.array(nose)
    # Tính toán góc pitch sử dụng vector từ mũi đến giữa hai mắt và từ mũi đến giữa hai miệng
    pitch_angle_eye = np.degrees(np.arctan2(nose_to_mid_eye_vector[1], nose_to_mid_eye_vector[0]))
    pitch_angle_mouth = np.degrees(np.arctan2(nose_to_mid_mouth_vector[1], nose_to_mid_mouth_vector[0]))

    # Trung bình hai góc để có kết quả tốt hơn
    pitch_angle = (pitch_angle_eye + pitch_angle_mouth) / 2
    return pitch_angle

# direction 0,1,2,3,4 (center, left, right, up, down)
def processImage(img,id,direction):
    print("Process Image Start ...")
    results_sc = app_sc.get(img)
    res = False
    if len(results_sc) < 1:
        return res

    face = results_sc[0]
    landmarks = face.kps
    angR = npAngle(landmarks[0], landmarks[1], landmarks[2])  # Calculate the right eye angle
    angL = npAngle(landmarks[1], landmarks[0], landmarks[2])  # Calculate the left eye angle
    if ((int(angR) in range(35, 57)) and (int(angL) in range(35, 58))):
        dir_face = 0
    else: 
        if angR < angL:
            dir_face = 1
        else:
            dir_face = 2

    pitch_angle = calculate_pitch(landmarks)
    if pitch_angle < 89:
        dir_face_ud = 3
    elif pitch_angle > 89:
        dir_face_ud = 4
    else:
        dir_face_ud = 5
    print(f"Dir Face: {dir_face}, {direction}")

    if direction >=3:
        if direction == dir_face_ud:
            print("Direction True")
            saveImage(img,id,direction)
            res = True
        else:
            print("Direction False")
    else:

        if direction == dir_face:
            saveImage(img,id,direction)
            res = True
        else:
            print("Direction False")
    
    print("Process Image End ...")
    return res
    

def detectDirectionFace(img,id,lstFaceDirection):
    print("Detect Direction Face Start ...")
    status = False
    message = "Huong khuon mat da ton tai"

    results_sc = app_sc.get(img)
    res = False
    if len(results_sc) < 1:
        return res

    face = results_sc[0]
    landmarks = face.kps
    angR = npAngle(landmarks[0], landmarks[1], landmarks[2])  # Calculate the right eye angle
    angL = npAngle(landmarks[1], landmarks[0], landmarks[2])  # Calculate the left eye angle
    if ((int(angR) in range(35, 57)) and (int(angL) in range(35, 58))):
        dir_face = 0
    else: 
        if angR < angL:
            dir_face = 1
        else:
            dir_face = 2
    
    required_directions = {0, 1, 2}
    if required_directions.issubset(lstFaceDirection):
        pitch_angle = calculate_pitch(landmarks)
        if pitch_angle < 89:
            dir_face = 3
        elif pitch_angle > 89:
            dir_face = 4
        else:
            dir_face = 5
    if dir_face not in lstFaceDirection:
        status = True
        message = "Huong khuon mat chua ton tai, Bat dau luu Hinh Anh"
        saveImage(img,id,dir_face)
    print("Detect Direction Face End ...")
    return dir_face, status, message


def saveImage(img,id,directionFace):
    print("Save Image Start ...")
    # Đảm bảo thư mục images tồn tại
    folderName = f"website/images/{id}"
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    filename = f"{directionFace}.png"
    # Lưu hình ảnh vào thư mục images với tên file được cung cấp
    
    cv2.imwrite(os.path.join(folderName, filename),img)
    print("Save Image End ... ")

def getIdLastest():
    cur = mysql.connection.cursor()
    cur.execute("SELECT max(id) FROM account")
    data = cur.fetchall()
    print(data[0][0])
    cur.close()
    return data[0][0]

def insertAccount(username, email, phone):
    print("Insert start ...")
    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO account (username, email, phone)
        VALUES (%s, %s, %s)
    ''', (username, email, phone))
    mysql.connection.commit()
    cur.close()