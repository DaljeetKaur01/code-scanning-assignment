import os
import pymysql
import smtplib
import ssl
from email.message import EmailMessage
import urllib.request

# Securely fetch database credentials from environment variables
DB_HOST = os.getenv("DB_HOST", "mydatabase.com")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret123")

def get_user_input():
    """Safely retrieves user input."""
    return input('Enter your name: ').strip()

def send_email(to_email, subject, body):
    """Sends an email securely using SMTP instead of os.system."""
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = os.getenv("SMTP_USER", "noreply@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "emailpassword")

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
    """Retrieves data securely from an external API."""
    url = 'https://secure-api.com/get-data'  # Use HTTPS for security
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode()
            return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_db(data):
    """Safely inserts data into the database using parameterized queries."""
    connection = None
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database="mydatabase",
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            query = "INSERT INTO mytable (column1, column2) VALUES (%s, %s)"
            cursor.execute(query, (data, "Another Value"))
        connection.commit()
        print("Data saved successfully.")
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    user_input = get_user_input()
    data = get_data()
    if data:
        save_to_db(data)
    send_email('admin@example.com', 'User Input', user_input)
