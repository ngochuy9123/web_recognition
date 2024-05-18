import cv2
import face_recognition
import pickle
import os

folderPath = "website/images"
pathList = os.listdir(folderPath)
imgList=[]
personIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    personIds.append(os.path.splitext(path)[0])

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        print(img.shape)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encode = encodings[0]
            encodeList.append(encode)
        else:
            print("No face found in the image")

    return encodeList

print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,personIds]
print("Encoding Completed")

file = open("website/EncodeFile.p","wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Save")
