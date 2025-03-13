import smtplib
import imaplib
import email
import re
import time

Sender_Email = "your_email@example.com"  # Replace with your email
Key = "your_email_password"  # Replace with your email password

def email_notification(message):
    """Send an email notification to the user."""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(Sender_Email, Key)
            subject = "Temperature Alert"
            body = message
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(Sender_Email, Sender_Email, msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def check_user_reply():
    """Check the user's email reply for 'YES' or 'NO'."""
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(Sender_Email, Key)
        mail.select('inbox')

        # Search for the latest email
        status, messages = mail.search(None, 'ALL')
        latest_email_id = messages[0].split()[-1]

        # Fetch the email content
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            if "YES" in body.upper():
                                return "YES"
                            elif "NO" in body.upper():
                                return "NO"
        return "NO"
    except Exception as e:
        print(f"Error checking email reply: {e}")
        return "NO"