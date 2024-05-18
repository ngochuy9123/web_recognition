import cv2
import pickle
import numpy as np
import face_recognition

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

print("Loading Encode File ...")
file = open("EncodeFile.p","rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,personIds = encodeListKnownWithIds
print("Encode File Loaded")

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None, 0.25, 0.25)
    imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            color = (0,0,255)
            label = personIds[matchIndex]
            personId = personIds[matchIndex]

            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4, x2*4, y2*4, x1*4

            t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] - 3
            cv2.rectangle(img, (x1,y1), c2, [255,0,255], -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=1,lineType=cv2.LINE_AA)
        # else:
        #     color = (0,255,0)
        #     personId = "Unknow"
        # # print(personId)
        # # Scale the bounding box back to the original image size
        # y1, x2, y2, x1 = faceLoc
        # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

        # # Draw the bounding box
        # cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        # cv2.putText(img, personId, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)


    cv2.imshow("Face Recognition",img)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break