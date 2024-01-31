import datetime
import os
import time
import cv2
import pandas as pd
import pygame

pygame.mixer.init()


report_button_clicked = False
proceed_button_clicked = False

# Callback function for mouse events
def mouse_callback(event, x, y, flags, param):
    global report_button_clicked, proceed_button_clicked

    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if the mouse click is within the region of the "Report" button
        if 10 < x < 110 and 10 < y < 60:
            report_button_clicked = True
        # Check if the mouse click is within the region of the "Proceed" button
        elif 130 < x < 230 and 10 < y < 60:
            proceed_button_clicked = True

def play_warning_audio(frame):
    global report_button_clicked, proceed_button_clicked

    # Load a warning sound file (replace 'warning.mp3' with the actual filename)
    pygame.mixer.music.load('warning.mp3')
    pygame.mixer.music.play(-1)  # -1 means play in repeat mode

    # Display the frame with the warning and buttons
    while pygame.mixer.music.get_busy():
        warning_frame = frame.copy()

        # Draw "Report" button
        cv2.rectangle(warning_frame, (10, 10), (110, 60), (0, 0, 255), -1)
        cv2.putText(warning_frame, "Report", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw "Proceed" button
        cv2.rectangle(warning_frame, (130, 10), (230, 60), (0, 255, 0), -1)
        cv2.putText(warning_frame, "Proceed", (150, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('Warning Frame', warning_frame)
        cv2.setMouseCallback('Warning Frame', mouse_callback)
        cv2.waitKey(100) 

        if report_button_clicked:
            # Handle "Report" button click action
            print("Report button clicked!")
            report_button_clicked = False  # Reset button state
            # Add your report functionality here

        if proceed_button_clicked:
            # Handle "Proceed" button click action
            print("Proceed button clicked!")
            pygame.mixer.music.stop()  # Stop the warning loop
            break

        if cv2.waitKey(1) & 0xFF == ord('s'):  # Press 's' to stop the warning loop
            pygame.mixer.music.stop()
            break

def recognize_attendance():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("./TrainingImageLabel/Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("EmployeeDetails"+os.sep+"EmployeeDetails.csv")
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance_file = f"./Attendance/Attendance_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # Create the attendance file with the header
    with open(attendance_file, 'w') as file:
        file.write(','.join(col_names) + '\n')

    # Initialize and start real-time video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # set video width
    cam.set(4, 480)  # set video height
    # Define min window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        _, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(int(minW), int(minH)), flags=cv2.CASCADE_SCALE_IMAGE)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (10, 159, 255), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

            if conf < 70:
                play_warning_audio(im)

            if conf < 100:
                aa = df.loc[df['Id'] == Id]['Name'].values
                confstr = "  {0}%".format(round(100 - conf))
                tt = str(Id)+"-"+aa
            else:
                Id = '  Unknown  '
                tt = str(Id)
                confstr = "  {0}%".format(round(100 - conf))

            if (conf) > 60:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = str(aa)[2:-2]
                
                # Check if the ID already exists in the file
                attendance_df = pd.read_csv(attendance_file)
                if int(Id) not in attendance_df['Id'].values:
                    with open(attendance_file, 'a') as file:
                        file.write(f"{Id},{aa},{date},{timeStamp}\n")
                    print(f"Details captured for {aa} at {date} {timeStamp}")

                # Check if there are no other faces in the frame
                if len(faces) == 1:
                    cam.release()
                    cv2.destroyAllWindows()
                    return

            tt = str(tt)[2:-2]
            if (100-conf) > 45:
                tt = tt + " [Pass]"
                cv2.putText(im, str(tt), (x+5, y-5), font, 1, (255, 255, 255), 2)
            else:
                cv2.putText(im, str(tt), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

            if (100-conf) > 45:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 0), 1)
            elif (100-conf) > 50:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
            else:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)

        cv2.imshow('Attendance', im)
        if (cv2.waitKey(1) == ord('q')):
            break

    print("Attendance Successful")
    cv2.destroyAllWindows()

# Call the function
# recognize_attendance()
