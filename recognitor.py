import face_recognition
import cv2
import numpy as np
import os
import gspread
from datetime import datetime


gc = gspread.service_account(filename='service_account.json')
gsheet_key = "1Vh1INZCAvpwgm2fA5YslgLQwwosR2m0wjmiq0kbMBnc"
worksheet = gc.open_by_key(gsheet_key).sheet1

def create_row(name, col):
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    values_list = worksheet.col_values(1)
    worksheet.update_cell(len(values_list) + 1, 1, name)
    worksheet.update_cell(len(values_list) + 1, col, dt_string)

def update_row(row, col, dt_string):
    worksheet.update_cell(row, col, dt_string)

def get_col_index():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%y")
    col_index = None
    try:
        col_index = worksheet.find(dt_string)
    except: ""

    if col_index is not None:
        return col_index.col
    else:
        col_len = len(worksheet.row_values(1))
        worksheet.update_cell(1, col_len + 1, dt_string)
        return col_len + 1

def attendance(name):
    cell = None
    col = get_col_index()
    try:
        cell = worksheet.find(name)
    except: ""

    if cell is not None:
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        update_row(cell.row, col, dt_string)
    else:
        create_row(name, col)


video_capture = cv2.VideoCapture(0)

dir_name = "assets"
images_name_with_type = os.listdir(dir_name)

# mang chua ten
known_face_names = []
known_face_encodings = []

# lay ten tu file anh
def get_name(name_with_type):
    return os.path.splitext(name_with_type)[0]

# nap vao mang
known_face_names = list(map(get_name, images_name_with_type))

def load_images(dir_name):
    known_face_encodes = []
    for image in images_name_with_type:
        try:
            imgLoaded = face_recognition.load_image_file(f'{dir_name}/{image}')
            imgLoaded = cv2.cvtColor(imgLoaded, cv2.COLOR_BGR2RGB)
            img_encoded = face_recognition.face_encodings(imgLoaded)[0]
        except: continue

        known_face_encodes.append(img_encoded)
    return known_face_encodes

known_face_encodings = load_images(dir_name)

face_locations = []
face_encodes = []
face_names = []
process_this_frame = False

while True:
    _, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            match_index = np.argmin(face_distances)
            if matches[match_index]:
                name = known_face_names[match_index]
                attendance(name)
            face_names.append(name)
            process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('n'):
        process_this_frame = True

    if cv2.waitKey(3) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
