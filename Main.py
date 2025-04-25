from flask import Flask, jsonify, render_template
import atexit
import logging
import logging as logger
import THM2 as THM
import MotorFunction as Motor
import Freenove_DHT as dht_sensor
import LightManager as LM
import RFIDManager as RM
import ProfileManager as PM
from datetime import datetime


app = Flask(__name__)

try:
    logger.info("Initializing Light Manager...")
    light_success = LM.initialize()
    if light_success:
        logger.info("Light Manager initialized successfully")
    else:
        logger.warning("Light Manager initialization failed or had issues")
except Exception as e:
    logger.error(f"Error initializing Light Manager: {e}")
    light_success = False

try:
    logger.info("Initializing RFID Manager...")
    rfid_success = RM.initialize()
    if rfid_success:
        logger.info("RFID Manager initialized successfully")
    else:
        logger.warning("RFID Manager initialization may have issues")
except Exception as e:
    logger.error(f"Error initializing RFID Manager: {e}")
    rfid_success = False

try:
    Motor.toggle(False)
    THM.disableFan()
    logger.info("FAN NEEDS TO START OFF")
except Exception as e:
    logger.error(f"OFFF!!!!")
    
@app.route('/')
def index():
    """Render the index html page"""
    logger.info("Serving index.html")
    return render_template('indexv2.html')

@app.route('/temp-hum')
def get_TH_data():
    """Get temperature and humidity data"""
    try:
        data = THM.get_sensor_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting temperature data: {e}")
        return jsonify({
            'error': str(e),
            'temperature': 0,
            'humidity': 0,
            'fan': False,
            'email_sent': False,
            'temperature_threshold': PM.userTempThreshold
        })

@app.route('/light-data')
def get_light_data():
    """Get light intensity data"""
    try:
        data = LM.get_sensor_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting light data: {e}")
        return jsonify({
            'error': str(e),
            'light_intensity': 0,
            'led_status': 'OFF',
            'light_threshold': PM.userLightThreshold
        })

@app.route('/rfid-data')
def get_rfid_data():
    """Get RFID user profile data"""
    try:
        # First check if MQTT is still connected
        if rfid_success:
            RM.check_mqtt_connection()
        
        # Get RFID data
        rfid_data = RM.get_rfid_data()
        return jsonify(rfid_data)
    except Exception as e:
        logger.error(f"Error getting RFID data: {e}")
        # Return safe defaults on error
        return jsonify({
            'error': str(e),
            'rfid_tag': "",
            'user_id': "",
            'username': "Default User",
            'temperature_threshold': PM.userTempThreshold,
            'intensity_threshold': PM.userLightThreshold,
            'profile_image': "https://avatar.iran.liara.run/public/2",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
@app.route('/profile')
def get_profile_data():
    """Get current user profile data"""
    try:
        profile_data = PM.profileData()
        return jsonify(profile_data)
    except Exception as e:
        logger.error(f"Error getting profile data: {e}")
        return jsonify({
            'error': str(e),
            'userID': "",
            'data': {
                'username': "Default User",
                'temperature_threshold': 20,
                'intensity_threshold': 2000,
                'profile_image': "https://avatar.iran.liara.run/public/2"
            }
        })

@app.route('/toggle-off')
def fan_off():
    """Turn off the fan"""
    try:
        Motor.toggle(False)
        THM.disableFan()  # Make sure fan state is updated in THM
        logger.info("Fan turned off")
        return jsonify({"status": "Fan turned off", "success": True})
    except Exception as e:
        logger.error(f"Error turning fan off: {e}")
        return jsonify({"status": "Error", "error": str(e), "success": False})

@app.route('/email-status')
def get_email_status():
    """Get email notification status"""
    try:
        # Get both temperature and light email statuses
        light_data = LM.get_sensor_data()
        
        status = {
            'temp_email_sent': THM.email_sent,
            'light_email_sent': light_data.get('light_email_sent', False),
            'last_temp_email_time': THM.last_email_time if hasattr(THM, 'last_email_time') else None,
            'last_light_email_time': light_data.get('last_light_email_time', 0),
            'any_email_sent': THM.email_sent or light_data.get('light_email_sent', False)
        }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting email status: {e}")
        return jsonify({
            'error': str(e),
            'temp_email_sent': False,
            'light_email_sent': False,
            'any_email_sent': False
        })


# Cleanup GPIO on exit
def cleanup():
    """Clean up resources on exit"""
    try:
        logger.info("Cleaning up resources...")
        Motor.cleanup()
        LM.cleanup()
        RM.cleanup()
        logger.info("Cleanup complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

atexit.register(cleanup)

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server on http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Server shutting down due to keyboard interrupt")
        cleanup() 
        exit()
    except Exception as e:
        logger.error(f"Server error: {e}")
        cleanup()
        exit(1)