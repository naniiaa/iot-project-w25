import smtplib
import imaplib
import email
import re
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('email_manager')

Sender_Email = "seconddummytwo@gmail.com"  # Replace with your email
Key = "lugt toyl jqza ffag"  # Replace with your email password or passkey
Receiver_Email = "templatebuttondown@gmail.com" #"example@gmail.com"

def email_notification(message):
    """Send an email notification to the user."""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            logger.info("Connected to the SMTP server")

            # Log in to your account
            smtp.login(Sender_Email, Key)
            logger.info("Logged in successfully!")

            subject = "Temperature Alert"
            body = message
            msg = f"Subject: {subject}\n\n{body}"

            # Send email
            smtp.sendmail(Sender_Email, Receiver_Email, msg)
            logger.info("Email sent successfully!")
            return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def check_user_reply():
    """Check the user's email reply for 'YES' or 'NO'."""
    logger.info("Checking for email replies...")

    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(Sender_Email, Key)
        mail.select('inbox')

        # Search for the latest email
        status, messages = mail.search(None, 'ALL')
        latest_email_id = messages[0].split()[-1]

        if not messages[0]:
            logger.info("No new messages found")
            return "NO"
        
        status, messages = mail.search(None, 'ALL')
        latest_email_id = messages[0].split()[-1]

        # Fetch the email content
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                if "Temperature Alert" in msg.get("Subject",""):
                    logger.info("Found a reply to temp alert")

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                logger.info(f"Reply Content: {body[:100]}...")

                # If YES or NO in reply
                if (re.search("yes", body.lower())):
                    logger.info("User replied YES")
                    return "YES"
                
                # If reply found, but no YES, we return NO
                elif (re.search("no", body.lower())):
                    logger.info("User replied NO")
                    return "NO"
                
        logger.info("No relevant replies found")
        return "NO"
    
    except Exception as e:
        logger.info(f"Error checking email reply: {e}")
        return "NO"
