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
from .faceProcess import app_sc, detectFaceDirection,dataframe,updateDataframe,recognitionFaceWithInsight


auth = Blueprint('auth',__name__)


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
    print(f"LIst lay tu JS {lstFaceDirection}")
    # direction = int(request.form.get("faceDirection")) 
    if file.filename == '':
        return "No selected file", 400
    if file:
        file_stream = BytesIO(file.read())
        img = np.array(Image.open(file_stream))
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        idUser = getIdLastest()
        resultFaceDirection = faceForSignUp(img,idUser,lstFaceDirection)
        status = False

        print(f"Face Direction: {resultFaceDirection}")
        if resultFaceDirection == 0:
            id, status_recog_face = recognitionFaceWithInsight(img)
            if status_recog_face == 1:
                response = {
                    "faceDirection":resultFaceDirection,
                    "status":False,
                    "lstFaceDirection":lstFaceDirection,
                    "message":"Khuon mat da ton tai",
                }
                return jsonify(response)
            else:
                if resultFaceDirection not in lstFaceDirection and resultFaceDirection > -1:
                    status = True
                    checkSuccessSignUp(lstFaceDirection)

                print(f"Status: {status}")
                response = {
                    "faceDirection":resultFaceDirection,
                    "status":status,
                    "lstFaceDirection":lstFaceDirection
                }
                return jsonify(response)

        
    return "Failed to save image", 500

def faceForSignUp(img,id,lstFaceDirection):
    print("Detect Direction Face Start ...")
    dir_face= detectFaceDirection(img,lstFaceDirection)
    
    if dir_face not in lstFaceDirection:
        saveImage(img,id,dir_face)
    print("Detect Direction Face End ...")
    return dir_face

def saveImage(img,id,directionFace):
    folderName = f"website/images/{id}"
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    filename = f"{directionFace}.png"
    
    cv2.imwrite(os.path.join(folderName, filename),img)

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

def checkSuccessSignUp(lstFaceDirection):
    print("Start Update DataFrame")
    if(len(lstFaceDirection) == 5):
        updateDataframe()