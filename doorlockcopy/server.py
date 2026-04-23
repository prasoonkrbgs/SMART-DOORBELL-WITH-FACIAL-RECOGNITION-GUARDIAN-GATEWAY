from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import random
import smtplib
from email.message import EmailMessage

app = FastAPI()

# CORS (for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_FACES_DIR = "known_faces"
DB_PATH = "visitor_logs.db"

# Ensure known_faces directory exists
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

# In-memory OTP store
otp_store = {}

# Hardcoded admin email and app password (replace with env variables in production)
ADMIN_EMAIL = "b220404@skit.ac.in"
APP_PASSWORD = "sqij pfaz nvmo lgje"

# ---------------- OTP LOGIN ---------------- #

@app.post("/request-otp")
def request_otp():
    otp = str(random.randint(100000, 999999))
    otp_store["admin"] = otp

    msg = EmailMessage()
    msg["Subject"] = "Your OTP"
    msg["From"] = ADMIN_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg.set_content(f"Your OTP is {otp}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(ADMIN_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

    return {"message": "OTP sent"}


@app.post("/verify-otp")
def verify_otp(otp: str = Query(...)):
    if otp_store.get("admin") == otp:
        return {"status": "success"}
    return {"status": "failed"}


# ---------------- FACE MANAGEMENT ---------------- #

@app.get("/faces")
def get_faces():
    # Returns list of filenames without extensions
    faces = [os.path.splitext(f)[0] for f in os.listdir(KNOWN_FACES_DIR) if f.endswith(".jpg")]
    return {"faces": faces}


@app.post("/faces/add")
async def add_face(name: str = Form(...), file: UploadFile = File(...)):
    # Save file as JPG
    path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"message": "Face added"}


@app.delete("/faces/{name}")
def delete_face(name: str):
    path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    if os.path.exists(path):
        os.remove(path)
        return {"message": "Deleted"}
    return {"error": "Not found"}


# ---------------- LOGS ---------------- #

@app.get("/logs")
def get_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    rows = cursor.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()
    conn.close()

    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "name": row[1],
            "image": row[2],        # keep but don't use in frontend
            "timestamp": row[3],    # ✅ correct timestamp
            "status": row[4] if len(row) > 4 else ("Denied" if row[1] == "Unknown" else "Granted")
        })

    return {"logs": logs}
