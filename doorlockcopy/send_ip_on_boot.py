#!/usr/bin/env python3
import subprocess
import time
import smtplib
import os
from email.message import EmailMessage

# ---------------- CONFIG ---------------- #
SENDER_EMAIL = "b220404@skit.ac.in"       # replace with your email
RECEIVER_EMAIL = "b220404@skit.ac.in"    # replace with your email
APP_PASSWORD = "sqij pfaz nvmo lgje"        # Gmail App Password
IP_FILE = os.path.join(os.path.dirname(__file__), "last_ip.txt")      # Flag to avoid multiple emails

# ---------------- INTERNET CHECK ---------------- #
import socket
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# ---------------- GET IP ADDRESS ---------------- #
def get_ip_address():
    try:
        # Run hostname -I exactly like command line
        ips = subprocess.check_output("hostname -I", shell=True).decode().strip()
        return ips
    except Exception:
        return "Unable to get IP"

# ---------------- SEND EMAIL ---------------- #
def send_ip_email(ip_addresses):
    print("Sending IP email...")

    msg = EmailMessage()
    msg["Subject"] = "Raspberry Pi Online - IP Address"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.set_content(f"""
Raspberry Pi is now ONLINE ✅

IP Address(es): {ip_addresses}

Time: {time.ctime()}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

    print("Email sent successfully")


# ---------------- MAIN ---------------- #
def main():
    print("Waiting for internet connection...")

    while not check_internet():
        print("No internet... retrying in 2 seconds")
        time.sleep(2)

    print("Internet connected")

    current_ip = get_ip_address()
    print("Current IP:", current_ip)

    # Check previous IP
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            old_ip = f.read().strip()

        if old_ip == current_ip:
            print("IP unchanged. Not sending email.")
            return

    # Send email if IP changed or first run
    send_ip_email(current_ip)

    # Save current IP
    with open(IP_FILE, "w") as f:
        f.write(current_ip)
        

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
