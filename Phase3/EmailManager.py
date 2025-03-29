import smtplib
import imaplib
import email
import re
import time
import logging
import paho.mqtt.client as mqtt
from datetime import date

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("email_manager")

Sender_Email = "centrobridjette@gmail.com"
Key = "fmhw shoy zuwx coqj"  # App password
Receiver_Email = "centrobridjette@gmail.com"

# MQTT Setup
MQTT_BROKER = "BROKER_IP_ADDRESS"  # Replace with actual broker IP
MQTT_PORT = 1883
MQTT_TOPIC_LIGHT = "sensor/light"
MQTT_TOPIC_EMAIL = "sensor/email"
LIGHT_THRESHOLD = 400  # Below this value, send an alert


def email_notification(message):
    """Send an email notification to the user."""
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            logger.info("Connected to the SMTP server")

            # Log in to your account
            smtp.login(Sender_Email, Key)
            logger.info("Logged in successfully!")

            subject = "Light Alert"
            body = message
            msg = f"Subject: {subject} {date.today()}\n\n{body}"

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
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(Sender_Email, Key)
        mail.select("inbox")

        # Search for the latest email
        status, messages = mail.search(None, "ALL")

        if not messages[0]:
            logger.info("No new messages found")
            return "NO"

        latest_email_id = messages[0].split()[-1]

        # Fetch the email content
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                if "Light Alert" in msg.get("Subject", ""):
                    logger.info("Found a reply to Light Alert")

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                logger.info(f"Reply Content: {body[:100]}...")

                # If YES or NO in reply
                if re.search("yes", body.lower()):
                    logger.info("User replied YES")
                    return "YES"

                elif re.search("no", body.lower()):
                    logger.info("User replied NO")
                    return "NO"

        logger.info("No relevant replies found")
        return "NO"

    except Exception as e:
        logger.error(f"Error checking email reply: {e}")
        return "NO"


# MQTT Callback when a message is received
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == MQTT_TOPIC_LIGHT:
        light_intensity = int(payload)
        logger.info(f"Received Light Intensity: {light_intensity}")

        if light_intensity < LIGHT_THRESHOLD:
            email_notification(f"Light intensity is too low: {light_intensity}. Do you want to turn off the alert?")
            client.publish(MQTT_TOPIC_EMAIL, "Email Sent")

    elif topic == MQTT_TOPIC_EMAIL:
        logger.info(f"Received email response: {payload}")

        if check_user_reply() == "YES":
            logger.info("User confirmed. Taking action.")
            # Perform action based on YES reply (e.g., stop further alerts)
        else:
            logger.info("No confirmation received. Keeping alert active.")


# MQTT Setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mqtt_client.subscribe(MQTT_TOPIC_LIGHT)
mqtt_client.subscribe(MQTT_TOPIC_EMAIL)

logger.info("Listening for MQTT messages...")
mqtt_client.loop_forever()


#pip install paho-mqtt smtplib RPi.GPIO
