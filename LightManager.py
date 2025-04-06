import time
import paho.mqtt.client as mqtt
import logging
import RPi.GPIO as GPIO
import EmailManager as EM
from datetime import datetime
from ProfileManager import userLightThreshold

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('light_manager')

# Constants
LIGHT_THRESHOLD = userLightThreshold  # Default threshold
LED_PIN = 12    # GPIO pin for LED

# MQTT Setup
MQTT_BROKER = "192.168.1.29" # "172.20.10.4"  # Replace with your broker IP
MQTT_PORT = 1883
MQTT_TOPIC_LIGHT = "sensor/light"
MQTT_TOPIC_LED = "sensor/led"

# Variables for tracking
light_intensity = 1000  # Initial value (above threshold)
led_status = "OFF"      # Initial LED status
mqtt_client = None      # MQTT client instance

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    logger.info(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to topics
    client.subscribe(MQTT_TOPIC_LIGHT)
    client.subscribe(MQTT_TOPIC_LED)

def on_message(client, userdata, msg):
    """Callback when a message is received"""
    global light_intensity, led_status
    
    topic = msg.topic
    payload = msg.payload.decode()
    
    logger.info(f"Received message on {topic}: {payload}")
    
    if topic == MQTT_TOPIC_LIGHT:
        try:
            # Update light intensity value
            light_intensity = int(payload)
            logger.info(f"Updated light intensity: {light_intensity}")
            
            # Check threshold and control LED
            check_light_threshold()
                
        except ValueError:
            logger.error(f"Could not convert light intensity value: {payload}")
    
    elif topic == MQTT_TOPIC_LED:
        # Handle LED control from ESP32 or other sources
        if payload == "ON":
            set_led(True)
            logger.info("LED turned ON from MQTT message")
        elif payload == "OFF":
            set_led(False)
            logger.info("LED turned OFF from MQTT message")

def check_light_threshold():
    """Check light intensity against threshold and take action"""
    global light_intensity, led_status
    
    # Get current email status
    email_status = EM.get_email_status('LIGHT')
    
    if light_intensity < LIGHT_THRESHOLD:
        set_led(True)  # Turn on LED
        
        # Check if we need to send an email
        if not email_status.get('status', False):
            # Get formatted time for email
            now = EM.get_formatted_time()
            
            # Send email notification
            msg = f"The Light is ON at {now} time. Current light intensity: {light_intensity}. This is below the threshold of {LIGHT_THRESHOLD}."
            EM.email_notification(msg, email_type='LIGHT')
    else:
        set_led(False)  # Turn off LED
        
        # Reset email status after cooldown period if light is above threshold
        if email_status.get('status', False):
            current_time = time.time()
            cooldown = email_status.get('cooldown', 300)
            last_sent = email_status.get('last_sent', 0)
            
            if current_time - last_sent > cooldown:
                EM.reset_email_status('LIGHT')

def set_led(state):
    """Set the LED state with results such as True to turn on, False to turn off"""
    global led_status
    
    try:
        if state:
            led_status = "ON"
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            led_status = "OFF"
            GPIO.output(LED_PIN, GPIO.LOW)
    except Exception as e:
        logger.error(f"Error setting LED state: {e}")

def get_sensor_data():
    """Return current light sensor data and status"""
    global light_intensity, led_status
    
    # Get email status
    email_status = EM.get_email_status('LIGHT')
    
    return {
        'light_intensity': light_intensity,
        'led_status': led_status,
        'light_email_sent': email_status.get('status', False),
        'last_light_email_time': email_status.get('last_sent', 0),
        'light_threshold': LIGHT_THRESHOLD,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def initialize():
    """Initialize MQTT client and GPIO"""
    global mqtt_client
    
    # Set up GPIO
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)  # Start with LED off
    logger.info(f"GPIO initialized with LED on pin {LED_PIN}")
    
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
    
    # Clean up GPIO for LED
    try:
        GPIO.cleanup(LED_PIN)
        logger.info("LED GPIO pin cleaned up")
    except:
        pass  # Ignore errors during cleanup
