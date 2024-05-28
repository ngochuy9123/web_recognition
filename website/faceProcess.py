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

def detectFaceDirection():
    print("Detect face direction start ...")
    
    print("Detect face direction end ...")

def recognitionFaceWithInsight():
    print("Face Recognition Start ...")
    
    print("Face Recognitin End ...")

def imgProcess(img):
    print("Img Process Start ...")

    print("Img Process End ...")


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

print("Hello")

