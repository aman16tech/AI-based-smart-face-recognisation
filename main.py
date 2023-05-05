import face_recognition
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os

# Load known faces and their names from images in a directory
known_faces_dir = r'E:\AIsystem\Face-Recognition-Attendance-Projects-main\Training_images\unknown_face'
known_face_encodings = []
known_face_names = []

print(known_faces_dir)
print(known_face_encodings)
print(known_face_names)

for filename in os.listdir(known_faces_dir):
    image = face_recognition.load_image_file(os.path.join(known_faces_dir, filename))
    face_encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(face_encoding)
    known_face_names.append(os.path.splitext(filename)[0])

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
attendance = []

ipaddress="http://192.168.0.102:8080"
# Load video capture device
cap = cv2.VideoCapture(0)

#for external cameras
#ipaddress="rtsp://192.168.0.102:8080"
#cap.read(ipaddress)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize frame to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # If a match was found in known_face_encodings, use the first one
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        face_names.append(name)

        if name not in attendance:
            attendance.append(name)
        # Add the name of the recognized person to the attendance list
        # attendance.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Release video capture device
cap.release()
cv2.destroyAllWindows()

# Save attendance list to an Excel file
attendance_df = pd.DataFrame({'Name': attendance, 'Time': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(attendance)})

# Get today's date in YYYY-MM-DD format
today = datetime.today().strftime('%Y-%m-%d')

# Append the date to the filename

filename = os.path.join("E:\AIsystem\Face-Recognition-Attendance-Projects-main", f'Attendance_{today}.xlsx')

attendance_df.to_excel(filename, index=False)