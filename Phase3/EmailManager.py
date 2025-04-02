import smtplib
import imaplib
import email
import re
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("email_manager")

Sender_Email = "centrobridjette@gmail.com"
Key = "fmhw shoy zuwx coqj"  # App password
Receiver_Email = "centrobridjette@gmail.com"

# Email Types and Status Tracking
EMAIL_TYPES = {
    'TEMPERATURE': {
        'subject': 'Temperature Alert',
        'cooldown': 300,  # No minutes cooldown between temperature emails
        'last_sent': 0,
        'status': False
    },
    'LIGHT': {
        'subject': 'Light Alert',
        'cooldown': 300,  # No minutes cooldown between light emails
        'last_sent': 0,
        'status': False
    }
}

def email_notification(message, subject=None, email_type = 'TEMPERATURE'):
    """Send an email notification to the user."""

        # Validate email type
    if email_type not in EMAIL_TYPES:
        logger.error(f"Invalid email type: {email_type}")
        return False
    
    # Use default subject if none provided
    if subject is None:
        subject = EMAIL_TYPES[email_type]['subject']
    
    # Check cooldown period
    current_time = time.time()

    if EMAIL_TYPES[email_type]['status'] and (current_time - EMAIL_TYPES[email_type]['last_sent'] < EMAIL_TYPES[email_type]['cooldown']):
        logger.info(f"Email cooldown active for {email_type}. Skipping notification.")
        return False
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            logger.info("Connected to the SMTP server")

            # Log in to your account
            smtp.login(Sender_Email, Key)
            logger.info("Logged in successfully!")

            current_date = datetime.now().strftime("%Y-%m-%d")

            # Format email
            formatted_msg = f"Subject: {subject} {current_date}\n\n{message}"

            # Send email
            smtp.sendmail(Sender_Email, Receiver_Email, formatted_msg)
            logger.info(f"{email_type} sent successfully!")

            # Update status
            EMAIL_TYPES[email_type]['status'] = True
            EMAIL_TYPES[email_type]['last_sent'] = current_time

            return True
        
    except Exception as e:
        logger.error(f"Error sending {email_type}: {e}")
        return False

def check_user_reply(email_type='TEMPERATURE'):
    """Check the user's email reply for 'YES' or 'NO'."""
    logger.info(f"Checking for {email_type} replies...")

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

                # if "Temperature Alert" in msg.get("Subject",""):
                #     logger.info("Found a reply to temperature alert")

                subject = msg.get("Subject", "")
                if EMAIL_TYPES[email_type]['subject'] not in subject:
                    logger.info(f"Latest email is not a {email_type} reply")
                    continue

                logger.info(f"Found a reply to {email_type} alert")

                # Get email body
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


def reset_email_status(email_type='TEMPERATURE'):
    """Reset the sent status for a specific email type"""
    if email_type not in EMAIL_TYPES:
        logger.error(f"Invalid email type: {email_type}")
        return False
    
    EMAIL_TYPES[email_type]['status'] = False
    logger.info(f"Reset {email_type} email status")
    return True

def get_email_status(email_type=None):
    """Get email status for one or all email types"""
    if email_type is not None:
        if email_type not in EMAIL_TYPES:
            logger.error(f"Invalid email type: {email_type}")
            return {}
        
        return {
            'status': EMAIL_TYPES[email_type]['status'],
            'last_sent': EMAIL_TYPES[email_type]['last_sent'],
            'cooldown': EMAIL_TYPES[email_type]['cooldown']
        }
    else:
        # Return all email statuses
        result = {}
        for type_name, type_data in EMAIL_TYPES.items():
            result[type_name.lower()] = {
                'status': type_data['status'],
                'last_sent': type_data['last_sent'],
                'cooldown': type_data['cooldown']
            }
        return result

def get_formatted_time():
    """Get the current time formatted as HH:MM"""
    return datetime.now().strftime("%H:%M")
