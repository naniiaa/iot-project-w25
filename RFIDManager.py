import paho.mqtt.client as mqtt
import logging
import time
from datetime import datetime
import ProfileManager
import EmailManager as EM

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rfid_manager')

# MQTT Setup - use the same broker IP as in ESP32 code
MQTT_BROKER = "192.168.1.29"  # Replace with your broker IP (same as in ESP32)
MQTT_PORT = 1883
MQTT_TOPIC_RFID = "rfid/ID"  # Same topic the ESP32 publishes to

# Variables for tracking
last_rfid_tag = ""
mqtt_client = None

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    logger.info(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to RFID topic
    client.subscribe(MQTT_TOPIC_RFID)

def on_message(client, userdata, msg):
    """Callback when a message is received"""
    global last_rfid_tag
    
    topic = msg.topic
    payload = msg.payload.decode()
    
    logger.info(f"Received message on {topic}: {payload}")
    
    if topic == MQTT_TOPIC_RFID:
        try:
            # Update RFID tag value
            rfid_tag = payload.strip().lower()  # Normalize the tag ID
            last_rfid_tag = rfid_tag
            logger.info(f"Updated RFID tag: {last_rfid_tag}")
            
            # Process the RFID tag
            process_rfid_tag(rfid_tag)
                
        except Exception as e:
            logger.error(f"Error processing RFID tag: {e}")

def process_rfid_tag(rfid_tag):
    """Process RFID tag and update user profile"""
    # Check if the tag exists in the profile database
    if rfid_tag in ProfileManager.profile_database:
        # Set the user profile
        ProfileManager.set_UserID(rfid_tag)
        
        # Get user information
        user_profile = ProfileManager.profile_database[rfid_tag]
        username = user_profile["username"]
        
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send email notification
        message = f"User {username} entered at {current_time}"
        subject = f"User Entry: {username}"
        EM.email_notification(message, subject=subject, email_type='RFID')
        
        logger.info(f"User {username} entered at {current_time}")
        return True
    else:
        logger.warning(f"RFID tag {rfid_tag} not found in profile database")
        return False

def get_rfid_data():
    """Return current RFID data and user profile information"""
    global last_rfid_tag
    
    user_id = ProfileManager.userID
    user_data = ProfileManager.profileData()
    
    return {
        'rfid_tag': last_rfid_tag,
        'user_id': user_id,
        'username': user_data.get('data', {}).get('username', 'Unknown'),
        'temperature_threshold': user_data.get('data', {}).get('temperature_threshold', 0),
        'intensity_threshold': user_data.get('data', {}).get('intensity_threshold', 0),
        'profile_image': user_data.get('data', {}).get('profile_image', ''),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def initialize():
    """Initialize MQTT client"""
    global mqtt_client
    
    # Set up MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()  # Start the loop in a background thread
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return False

def cleanup():
    """Clean up resources"""
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()