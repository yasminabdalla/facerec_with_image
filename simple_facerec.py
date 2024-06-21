import face_recognition
import cv2
import os
import glob
import numpy as np

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path: Path to the images
        """
        # Get list of images in the specified path
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        print("{} encoding images found.".format(len(images_path)))

        for img_path in images_path:
            # Load the image
            img = face_recognition.load_image_file(img_path)
            if img is None:
                print(f"Could not read image {img_path}")
                continue
            
            # Convert image to RGB
            try:
                if img.shape[2] == 4:  # If the image has an alpha channel
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                elif img.shape[2] == 3:  # If the image is in BGR format
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                else:
                    print(f"Unsupported image format: {img_path}")
                    continue
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")
                continue

            # Extract filename without extension
            basename = os.path.basename(img_path)
            filename, ext = os.path.splitext(basename)
            
            # Get face encodings
            img_encoding = face_recognition.face_encodings(img)
            if len(img_encoding) == 0:
                print(f"No face encodings found in {img_path}")
                continue

            # Store face encoding and corresponding name
            self.known_face_encodings.append(img_encoding[0])
            self.known_face_names.append(filename)
        print("Encoding images loaded")

    def detect_known_faces(self, frame):
        """
        Detect known faces in a given frame
        :param frame: Frame from video or camera
        :return: Tuple of face locations and face names
        """
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)

        # Adjust face locations according to the frame resizing
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names
