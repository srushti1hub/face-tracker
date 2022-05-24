# CLI Application
# Importing necessary libraries
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# FUNCTIONS :
# This function encodes the images present in images folder
def faceEncodings(images):
    encodeList = []
    print("\nEncoding...\n")
    for i in images:
        i = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(i)[0]
        encodeList.append(encode)
    return encodeList


# This function marks the attendance along with name,date,time in google sheet
def markAttendance(name):

    # If the person is already marked present in the sheets no action is taken
    if attendanceList.__contains__(name):
        return 0

    # Otherwise his/her attendance is marked in google sheet
    else:
        attendanceList.append(name)
        cur_date = datetime.now().strftime('%d-%m-%Y')
        cur_time = datetime.now().strftime('%H:%M:%S')
        record = [name, cur_date, cur_time]
        sheet.append_row(record)
        print("Hey, "+name+" Your Attendance is Marked")


# DRIVER CODE :
path = "images"
# array to store images
images = []
# array to store names
personName = []
myList = os.listdir(path)
# stores the current attendee names
attendanceList = []

for i in myList:
    current_image = cv2.imread(f'{path}/{i}')
    images.append(current_image)
    personName.append(os.path.splitext(i)[0])

print("Student List : ")
print(personName)

# encoding already present images
encodeListKnown = faceEncodings(images)
print(encodeListKnown)
print("\nEncoding Completed !\n")

# Connecting the Google account and service account with APIs
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("my-project-71428-350612-b42540ba3b1c.json", scope)
client = gspread.authorize(creds)

# Opening the Google sheet
sheet = client.open("Attendance").sheet1

# Deleting past attendance details
no_of_records = len(sheet.get_all_values())
sheet.delete_rows(2, no_of_records)


# Capturing images from laptop webcam
# NOTE : If you are using external camera then use capture = cv2.VideoCapture(1)
capture = cv2.VideoCapture(0)

# Infinite loop to capture images from webcam till application is quit
while True:
    # Capturing and encoding current images from current frame
    ret, frame = capture.read()
    faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)
    facesCurrentFrame = face_recognition.face_locations(faces)
    encodeCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

    # Comparing images in our system and images from webcam
    for encodeFace, faceLoc in zip(encodeCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDistance)

        # If match is found then name along with rectangular frame is displayed in screen
        if matches[matchIndex]:
            name = personName[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

            # Code to display rectangle and name of the known person
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    # If q key is pressed , application closes
    cv2.imshow("Webcam", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

# Turning off webcam
capture.release()
cv2.destroyAllWindows()
