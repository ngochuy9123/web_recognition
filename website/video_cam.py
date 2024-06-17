from flask import Flask, Response, Blueprint, render_template,request,jsonify
import cv2
from .faceProcess import getImages,ml_search_algorithm,app_sc,dataframe
import base64
from PIL import Image
import json
import time

video_cam = Blueprint('video_cam',__name__)
recognized_persons = []

@video_cam.route('/face_recog_cam')
def video_home():
    return render_template("recog_cam.html")

@video_cam.route('/face_recog_cam', methods=["POST"])
def face_recog_cam():
    # return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    data = request.get_json()
    if not data or 'rstp' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    rstp = data['rstp']
    print(f'Received URL: {rstp}')

    frame_base64 = generate_frame(rstp)
    if frame_base64 is None:
        return jsonify({'error': 'Failed to capture image from the provided RTSP URL'}), 400
    
    
    return Response(generate_frame(rstp), mimetype='multipart/x-mixed-replace; boundary=frame')

def img_process(img):
    down_points = (640, 512)
    img = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
    h,w,c = img.shape
    return img

def generate_frame(rstp):
    # Thay thế bằng link RTSP của bạn
    camera = cv2.VideoCapture(rstp)
    global recognized_persons
    recognized_persons = []


    if not camera.isOpened():
        print("Error: Could not open video stream")
        return None
    while True:
        success, frame = camera.read()
        frame = img_process(frame)
        if not success:
            break
        else:
            results_sc = app_sc.get(frame)
            current_persons = []
            for res in results_sc:
                x1,y1,x2,y2 = res['bbox'].astype(int)
                emmbeddings = res['embedding']
                person_name = ml_search_algorithm(dataframe, "Facial_Features", test_vector=emmbeddings, name=["Name"],thresh=0.4)
                if str(person_name) == "Unknown":
                    color = (0,0,255)
                    text_gen =  person_name
                    
                else:
                    color = (0,255,0)
                    text_gen =  person_name
                current_persons.append(text_gen)
                cv2.rectangle(frame,(x1,y1),(x2,y2),color)
                cv2.putText(frame,text_gen ,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.5,color,1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')

            recognized_persons = list(current_persons)

            
            yield (b'--frame\r\n'
                 b'Content-Type: text/plain\r\n\r\n' + frame_base64.encode() + b'\r\n')
            

@video_cam.route('/recognized_persons', methods=["GET"])
def get_recognized_persons():
    global recognized_persons
    return jsonify({'persons': recognized_persons})