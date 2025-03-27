import os
import pymysql
import smtplib
import ssl
from email.message import EmailMessage
import urllib.request

# Environment variables for security
DB_HOST = os.getenv("DB_HOST", "mydatabase.com")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # No default value for password!

def get_user_input():
    """Safely retrieves user input with sanitization."""
    return input('Enter your name: ').strip()

def send_email(to_email, subject, body):
    """Secure email sending with TLS and env vars."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_user, smtp_password]):
        raise ValueError("SMTP credentials not configured")

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_data():
    """Secure API request with timeout and HTTPS."""
    url = 'https://secure-api.com/get-data'
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                return response.read().decode()
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_db(data):
    """Secure DB connection with error handling."""
    connection = None
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database="mydatabase",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        with connection.cursor() as cursor:
            query = "INSERT INTO mytable (column1, column2) VALUES (%s, %s)"
            cursor.execute(query, (data, "Another Value"))
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    try:
        user_input = get_user_input()
        data = get_data()
        if data:
            save_to_db(data)
        send_email('admin@example.com', 'User Input', user_input)
    except Exception as e:
        print(f"Application error: {e}")