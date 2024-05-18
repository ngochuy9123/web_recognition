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
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,personIds]
print("Encoding Completed")

file = open("website/EncodeFile.p","wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Save")
