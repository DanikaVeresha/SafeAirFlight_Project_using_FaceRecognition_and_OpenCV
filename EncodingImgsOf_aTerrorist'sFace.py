import cv2
import face_recognition
from imutils import paths
import pickle
import os


imagePaths = list(paths.list_images('Terrorist photo collection'))
#It is assumed that many folders with the names of potentially threatening persons can
# be uploaded to this directory
knownEncodings = []
knownNames = []

for (item, imagePath) in enumerate(imagePaths):
    name = imagePath.split(os.path.sep)[-2]
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model='hog')
    encodings = face_recognition.face_encodings(rgb, boxes)
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)
        data = {
            'encodings': knownEncodings,
            'names': knownNames
        }
        f = open('face_enc_terrorist', 'wb')
        f.write(pickle.dumps(data))
        f.close()

