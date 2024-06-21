import cv2
from simple_facerec import SimpleFacerec
from fastapi import FastAPI, HTTPException, Response
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'homex-fd825.appspot.com'})
bucket = storage.bucket()

# Initialize FastAPI
app = FastAPI()
sfr = SimpleFacerec()
sfr.load_encoding_images("Trainingimages/")

def url_to_image():
    blob = bucket.get_blob("data/photo.jpg")  # Get the blob from Firebase
    arr = np.frombuffer(blob.download_as_string(), np.uint8)  # Convert blob to array of bytes
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # Decode array to an image
    return img

@app.get("/")
def home():
    return {"health_check": "OK", "model_version": '1.0'}

@app.get('/face_recognition')
def return_names():
    img = url_to_image()  # Get the image from Firebase
    
    # Perform face recognition
    faces, face_names = sfr.detect_known_faces(img)
    
    # Annotate the image with recognized names (optional)
    annotated_img = img.copy()
    for face_loc, name in zip(faces, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        cv2.putText(annotated_img, name, (x1, y2 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 200, 0), 4)

    # Encode the image to PNG format
    _, img_encoded = cv2.imencode('.png', annotated_img)
    img_bytes = img_encoded.tobytes()

    # Return both the PNG image and the detected face names
    return Response(content=img_bytes, media_type='image/png')
