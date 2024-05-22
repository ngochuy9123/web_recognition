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


process_img = Blueprint('process_img',__name__)


folderModel = "indightface_models/"
app_sc = FaceAnalysis(name='buffalo_sc', 
                     root = "insightface_model",
                     providers=['CPUExecutionProvider'])
app_sc.prepare(ctx_id = 0, det_size=(640,640))


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

    return "Failed to save image", 500

def getIdFromName(name):
    return name.split("_")[0]
def img_process(img):
    down_points = (640, 512)
    img = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
    h,w,c = img.shape
    return img
def getImages(folder_img, faceapp):
    person_info = []
    listdir =os.listdir(path=folder_img)
    for folder_name in listdir:
        name = folder_name
        img_files = os.listdir(path=f'{folder_img}/{folder_name}')
        for file in img_files:
            path = f'website/images/{folder_name}/{file}'
            img_arr = cv2.imread(path)
            result = faceapp.get(img_arr, max_num=1)
            if len(result)>0:
                res = result[0]
                emmbedding = res['embedding']
                person_info.append([name,emmbedding])
    dataframe  =pd.DataFrame(person_info, columns=['Name','Facial_Features'])
    return dataframe
def ml_search_algorithm(dataframe, feature_column, test_vector, name=["Name"], thresh=0.5):
    dataframe = dataframe.copy()

    X_list = dataframe[feature_column].tolist()
    x=np.asarray(X_list)

    similar = pairwise.cosine_similarity(x,test_vector.reshape(1,-1))
    similar_arr =  np.array(similar).flatten()
    dataframe['cosine'] = similar_arr

    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter)>0:
        data_filter.reset_index(drop=True,inplace=True)
        argmax = data_filter['cosine'].argmax()
        
        person_name = data_filter.iloc[argmax]["Name"]
    else:
        person_name = 'Unknown'
    
    return person_name

path_folder_img = "website/images"
dataframe = getImages(path_folder_img, app_sc)

def face_recog_by_insightface(img):
    userid = 0
    status = 0

    img = img_process(img)
    print(img.shape)
    results_sc = app_sc.get(img)
    img_copy = img.copy()
    for res in results_sc:
        x1,y1,x2,y2 = res['bbox'].astype(int)
        emmbeddings = res['embedding']
        person_name = ml_search_algorithm(dataframe, "Facial_Features", test_vector=emmbeddings, name=["Name"],thresh=0.5)
        if str(person_name) == "Unknown":
            color = (0,0,255)
            text_gen =  person_name
            userid = 0
        else:
            color = (0,255,0)
            text_gen =  person_name
            userid = int(person_name)
            status = 1
            # cur = mysql.connection.cursor()
            # cur.execute(f"SELECT * FROM account where id = {int(text_gen)}")
            # data = cur.fetchall()
            # print(data)
            # cur.close()

        # cv2.rectangle(img_copy,(x1,y1),(x2,y2),color)
        # cv2.putText(img_copy,text_gen ,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.5,color,1)

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

