import paho.mqtt.client as mqtt
import logging
import time
import traceback
from datetime import datetime
import ProfileManager as PM
import EmailManager as EM

# Set up enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("rfid_debug.log")
    ]
)
logger = logging.getLogger('rfid_manager')

# MQTT Setup
MQTT_BROKER = "10.0.0.230"  # MAtch this with ESP32
MQTT_PORT = 1883
MQTT_TOPIC_RFID = "rfid/ID"

last_rfid_tag = ""
last_entered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
mqtt_client = None
last_successful_connection = 0
reconnect_interval = 10  # seconds

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    global last_successful_connection
    
    if rc == 0:
        logger.info("Successfully connected to MQTT broker")
        last_successful_connection = time.time()
        
        # Subscribe to RFID topic
        client.subscribe(MQTT_TOPIC_RFID)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC_RFID}")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    logger.warning(f"Disconnected from MQTT broker with code {rc}")
    
    if rc != 0:
        logger.error("Unexpected disconnection, will attempt to reconnect")

def on_message(client, userdata, msg):
    """Callback when a message is received"""
    global last_rfid_tag, last_entered
    
    topic = msg.topic
    payload = msg.payload.decode().strip()
    
    logger.info(f"Received message on {topic}: {payload}")
    
    if topic == MQTT_TOPIC_RFID:
        try:
            # Update RFID tag value
            if payload:  # Check if payload is not empty
                last_rfid_tag = payload.lower()  
                logger.info(f"Updated RFID tag: {last_rfid_tag}, entered at: {last_entered}")
                
                # Process the RFID tag
                process_rfid_tag(last_rfid_tag)
            else:
                logger.warning("Received empty RFID payload")
        except Exception as e:
            logger.error(f"Error processing RFID tag: {e}")
            logger.error(traceback.format_exc())

def process_rfid_tag(rfid_tag):
    """Process RFID tag and update user profile"""
    try:
        # Update ProfileManager with the tag
        PM.set_UserID(rfid_tag)
        
        # Get user info after ID set
        user_data = PM.profileData()
        
        # Extract username with safe fallback
        username = user_data.get('data', {}).get('username', 'Unknown User')
        
        logger.info(f"Username retrieved: {username}")
        
        # Get current time
        # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send email notif
        message = f"User {username} entered at {last_entered} with RFID tag {rfid_tag}"
        subject = f"User Entry: {username}"
        
        try:
            email_sent = EM.email_notification(message, subject=subject, email_type='RFID')
            logger.info(f"Email notification sent for user {username}: {email_sent}")
        except Exception as email_error:
            logger.error(f"Error sending email notification: {email_error}")
        
        logger.info(f"User {username} entered at {last_entered}")
        return True
    except Exception as e:
        logger.error(f"Error in process_rfid_tag: {e}")
        logger.error(traceback.format_exc())
        return False

def get_rfid_data():
    """Return current RFID data and user profile information"""
    try:
        global last_rfid_tag
        
        # Retrieve current user ID and profile data
        user_id = PM.userID
        user_data = PM.profileData()

        # Extract profile data with safe fallbacks
        if isinstance(user_data, dict) and 'data' in user_data:
            profile_data = user_data.get('data', {})
            username = profile_data.get('username', 'Unknown')
            temp_threshold = profile_data.get('temperature_threshold', 0)
            intensity_threshold = profile_data.get('intensity_threshold', 0)
            profile_image = profile_data.get('profile_image', '')

        else:
            # Fallback for safety
            username = 'Unknown'
            temp_threshold = 0
            intensity_threshold = 0
            profile_image = ''
        
        # Create and return the data structure
        result = {
            'rfid_tag': last_rfid_tag,
            'user_id': user_id,
            'username': username,
            'temperature_threshold': temp_threshold,
            'intensity_threshold': intensity_threshold,
            'profile_image': profile_image,
            'timestamp': last_entered,
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in get_rfid_data: {e}")
        logger.error(traceback.format_exc())
        
        # Return safe defaults on error
        return {
            'rfid_tag': last_rfid_tag,
            'user_id': '',
            'username': 'Error',
            'temperature_threshold': 0,
            'intensity_threshold': 0,
            'profile_image': 'https://avatar.iran.liara.run/public/1',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': str(e)
        }

def check_mqtt_connection():
    """Check MQTT connection and reconnect if necessary"""
    global last_successful_connection
    
    if not mqtt_client:
        logger.warning("MQTT client not initialized")
        return False
        
    if not mqtt_client.is_connected():
        current_time = time.time()
        
        # Only try to reconnect 
        if current_time - last_successful_connection > reconnect_interval:
            logger.info("MQTT client disconnected, attempting to reconnect")
            try:
                mqtt_client.reconnect()
                return True
            except Exception as e:
                logger.error(f"Failed to reconnect to MQTT: {e}")
                last_successful_connection = current_time  # Update to prevent too frequent reconnection attempts
                return False
        return False
    return True

def initialize():
    """Initialize MQTT client with better error handling"""
    global mqtt_client
    
    try:
        # Set up MQTT client
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        
        try:
            # Connect to MQTT broker
            logger.info(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            # Start the loop in a background thread
            mqtt_client.loop_start()
            logger.info(f"MQTT client started for broker at {MQTT_BROKER}:{MQTT_PORT}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            logger.error(traceback.format_exc())
            return False
    except Exception as e:
        logger.error(f"Error initializing MQTT client: {e}")
        logger.error(traceback.format_exc())
        return False

def cleanup():
    """Clean up resources"""
    if mqtt_client:
        try:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            logger.info("MQTT client disconnected")
        except Exception as e:
            logger.error(f"Error during MQTT cleanup: {e}")
