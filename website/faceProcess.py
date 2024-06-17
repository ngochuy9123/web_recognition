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

folderModel = "indightface_models/"
app_sc = FaceAnalysis(name='buffalo_sc', 
                     root = "insightface_model",
                     providers=['CPUExecutionProvider'])
app_sc.prepare(ctx_id = 0, det_size=(640,640))

# dataframe = pd.DataFrame()

def getImageByAppSC(img):
    results_sc = app_sc.get(img)
    result = True
    if len(results_sc)< 1:
        result = False
    
    return results_sc,result

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

path_folder_img = "website/images"
dataframe = getImages(path_folder_img, app_sc)

def updateDataframe():
    global dataframe
    path_folder_img = "website/images"
    dataframe = getImages(path_folder_img, app_sc)


 

def ml_search_algorithm(dataframe, feature_column, test_vector, name=["Name"], thresh=0.5):
    # if len(dataframe)<1:

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

def detectFaceDirection(img,lstFaceDirection):
    results_sc,result = getImageByAppSC(img)
    res = -1
    if result == False:
        return res
    face = results_sc[0]
    landmarks = face.kps
    if len(lstFaceDirection) < 3:
        res = detectFaceDirectionLCR(landmarks)
    else:
        res = detectFaceDirectionUD(landmarks)
    print(f"Result Face Direction: {res}")
    return res

def detectFaceDirectionLCR(landmarks):
    angR = npAngle(landmarks[0], landmarks[1], landmarks[2])  # Calculate the right eye angle
    angL = npAngle(landmarks[1], landmarks[0], landmarks[2])  # Calculate the left eye angle
    if ((int(angR) in range(35, 57)) and (int(angL) in range(35, 58))):
        res = 0
    else: 
        if angR < angL:
            res = 1
        else:
            res = 2
    return res

def detectFaceDirectionUD(landmarks):
    pitch_angle = calculate_pitch(landmarks)
    if pitch_angle < 90.5:
        res = 3
    elif pitch_angle > 90.5:
        res = 4
    else:
        res = 5
    return res

def recognitionFaceWithInsight(img):
    userid = 0
    status = 0
    img = img_process(img)
    results_sc = app_sc.get(img)
    for res in results_sc:
        emmbeddings = res['embedding']
        person_name = ml_search_algorithm(dataframe, "Facial_Features", test_vector=emmbeddings, name=["Name"],thresh=0.5)
        if str(person_name) == "Unknown":
            userid = 0
            status = 0
        else:
            userid = int(person_name)
            status = 1

    return userid,status

def imgProcess(img):
    print("Image Process")


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

    nose_to_mid_eye_vector = np.array(nose) - np.array(mid_eye)
    nose_to_mid_mouth_vector = np.array(mid_mouth) - np.array(nose)

    pitch_angle_eye = np.degrees(np.arctan2(nose_to_mid_eye_vector[1], nose_to_mid_eye_vector[0]))
    pitch_angle_mouth = np.degrees(np.arctan2(nose_to_mid_mouth_vector[1], nose_to_mid_mouth_vector[0]))

    pitch_angle = (pitch_angle_eye + pitch_angle_mouth) / 2
    return pitch_angle




