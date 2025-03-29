import os
import pymysql
import smtplib
import ssl
import re
import time
from email.message import EmailMessage
import urllib.request

# Environment variables (set in GitHub Secrets)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # Required, no default!

def sanitize_input(input_str):
    """Allow only alphanumeric + spaces."""
    if not re.match(r"^[a-zA-Z0-9\s]+$", input_str):
        raise ValueError("Invalid input: Only letters/numbers allowed")
    return input_str.strip()

def get_user_input():
    """Securely get and sanitize user input."""
    try:
        user_input = input("Enter your name: ")
        return sanitize_input(user_input)
    except ValueError as e:
        print(f"Error: {e}")
        raise

def send_email(to_email, subject, body):
    """Send email with TLS and env vars."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_server, smtp_user, smtp_password]):
        raise ValueError("SMTP credentials missing")

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Email failed: {e}")
        raise

def get_data():
    """Secure API request with timeout + rate-limiting."""
    time.sleep(1)  # Rate-limit
    url = "https://secure-api.com/get-data"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                return response.read().decode()
    except Exception as e:
        print(f"API error: {e}")
        return None

def save_to_db(data):
    """Secure DB connection with parameterized queries."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database="mydb",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        with connection.cursor() as cursor:
            query = "INSERT INTO users (data) VALUES (%s)"
            cursor.execute(query, (data,))  # ✅ SQL injection-safe
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"DB error: {e}")
        raise
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    try:
        user_input = get_user_input()
        api_data = get_data()
        if api_data:
            save_to_db(api_data)
        send_email("admin@example.com", "New Data", user_input)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)