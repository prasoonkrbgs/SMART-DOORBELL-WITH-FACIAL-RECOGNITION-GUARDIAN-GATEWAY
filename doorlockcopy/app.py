print("initilization ongoing wait for some seconds")

import face_recognition
import cv2
import numpy as np
import os
import smtplib
import imghdr
from email.message import EmailMessage
import RPi.GPIO as GPIO
import time
import socket
import sqlite3
from datetime import datetime

# 1. PIN Setup and initialization
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GREEN_LED = 29
RED_LED = 31
SERVO_PIN = 32
BUZZER_PIN = 36
BUTTON_PIN = 33
PIR_PIN = 35

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIR_PIN, GPIO.IN)

# GPIO Startup State
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.HIGH)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# Servo PWM initialization
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)


# ---------------- INTERNET CHECK ---------------- #

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

print("Checking internet connection...")

while not check_internet():
    print("No internet... waiting")
    GPIO.output(RED_LED, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(RED_LED, GPIO.LOW)
    time.sleep(0.5)

print("Internet connected")
GPIO.output(RED_LED, GPIO.LOW)
time.sleep(0.5)
GPIO.output(RED_LED, GPIO.HIGH)

# ---------------- DATABASE SETUP ---------------- #

conn = sqlite3.connect("visitor_logs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

# ---------------- LOAD KNOWN FACES ---------------- #

KNOWN_FACES_DIR = "known_faces"

known_face_encodings = []
known_face_names = []

print("Loading known faces...")

for filename in os.listdir(KNOWN_FACES_DIR):

    if filename.endswith(".jpg") or filename.endswith(".png"):

        image_path = os.path.join(KNOWN_FACES_DIR, filename)

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_face_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)
            print(f"Loaded: {name}")

print("All faces loaded successfully.")

# ---------------- UTIL FUNCTIONS ---------------- #

def open_door():
    print("Opening door...")
    servo.ChangeDutyCycle(7)
    time.sleep(2)
    servo.ChangeDutyCycle(0)

    print("Door opened")
    time.sleep(5)

    print("Closing door...")
    servo.ChangeDutyCycle(2)
    time.sleep(2)
    servo.ChangeDutyCycle(0)

    print("Door closed")


def send_email(image_path, person_name):

    print("Sending email...")

    sender_email = "b220404@skit.ac.in"
    receiver_email = "b220404@skit.ac.in"
    password = "sqij pfaz nvmo lgje"

    msg = EmailMessage()
    msg["Subject"] = f"Visitor Detected: {person_name}"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"Visitor detected: {person_name}")

    with open(image_path, "rb") as f:
        img_data = f.read()
        img_type = imghdr.what(f.name)

    msg.add_attachment(
        img_data,
        maintype="image",
        subtype=img_type,
        filename="visitor.jpg"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, password)
        smtp.send_message(msg)

    print("Email sent successfully")


# ✅ FIXED: moved outside
def log_event(name, image_path):

    conn = sqlite3.connect("visitor_logs.db")
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO logs (name, image, timestamp)
        VALUES (?, ?, ?)
    """, (name, image_path, timestamp))

    conn.commit()
    conn.close()

    print("Log saved:", name, timestamp)

# ---------------- MAIN LOOP ---------------- #

print("Waiting for button press...")

GPIO.output(RED_LED, GPIO.LOW)

GPIO.output(BUZZER_PIN, GPIO.HIGH)
time.sleep(1)
GPIO.output(BUZZER_PIN, GPIO.LOW)

try:

    while True:

        if GPIO.input(BUTTON_PIN) == GPIO.LOW:

            print("Button pressed")

            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            
            # ✅ TURN CAMERA ON HERE
            video_capture = cv2.VideoCapture(0)
            time.sleep(2)

            if not video_capture.isOpened():
                print("Camera not detected")
                continue


            ret, frame = video_capture.read()
            # ✅ TURN CAMERA OFF IMMEDIATELY AFTER CAPTURE
            video_capture.release()

            if not ret:
                print("Camera error")
                continue

            os.makedirs("logs", exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"logs/visitor_{timestamp_str}.jpg"

            cv2.imwrite(image_path, frame)

            small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
            rgb_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            detected_name = "Unknown"

            for face_encoding in face_encodings:

                matches = face_recognition.compare_faces(
                    known_face_encodings,
                    face_encoding
                )

                face_distances = face_recognition.face_distance(
                    known_face_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    detected_name = known_face_names[best_match_index]

            print("Detected:", detected_name)

            if detected_name != "Unknown":

                print("Access Granted")
                GPIO.output(GREEN_LED, GPIO.HIGH)
                GPIO.output(RED_LED, GPIO.LOW)
                open_door()

            else:

                print("Access Denied")
                GPIO.output(GREEN_LED, GPIO.LOW)
                GPIO.output(RED_LED, GPIO.HIGH)

            # ✅ FIX: log for both cases
            log_event(detected_name, image_path)

            send_email(image_path, detected_name)

            time.sleep(5)

            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.LOW)

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nProgram interrupted by user (Ctrl+C)")

except Exception as e:
    print("Unexpected error:", e)

finally:
    print("Cleaning up GPIO and camera...")

    servo.stop()
    GPIO.cleanup()
    video_capture.release()
    cv2.destroyAllWindows()

    print("Shutdown complete")
