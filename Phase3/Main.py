from flask import Flask, jsonify, render_template
import atexit
# import TempHumManager as THM
import THM2 as THM
import MotorFunction as Motor
import Freenove_DHT as dht_sensor
import LightManager as LM

app = Flask(__name__)

LM.initialize()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp-hum')
def get_TH_data():
    return jsonify(THM.get_sensor_data())  # Grabs the DHT data and converts it into JSON

# @app.route('/light-data')
# def get_light_data():
#     return jsonify(LM.get_sensor_data())  # Grabs the light intensity data and converts it into JSON

@app.route('/light-data')
def get_light_data():
    """Get light intensity data"""
    try:
        return jsonify(LM.get_sensor_data())
    except Exception as e:
        logger.error(f"Error getting light data: {e}")
        return jsonify({
            'error': str(e),
            'light_intensity': None,
            'led_status': 'ERROR'
        })

@app.route('/toggle-off')
def fan_off():
    Motor.toggle(False)
    return jsonify({"status": "Fan turned off"})

# @app.route('/email-status')
# def get_email_status():
#     return jsonify({
#         'email_sent': THM.email_sent,
#         'last_email_time': THM.last_email_time if hasattr(THM, 'last_email_time') else None,
#     })

@app.route('/email-status')
def get_email_status():
    # Get both temperature and light email statuses
    light_data = LM.get_sensor_data()
    
    return jsonify({
        'temp_email_sent': THM.email_sent,
        'light_email_sent': light_data.get('light_email_sent', False),
        'last_temp_email_time': THM.last_email_time if hasattr(THM, 'last_email_time') else None,
        'last_light_email_time': light_data.get('last_light_email_time', 0),
        'any_email_sent': THM.email_sent or light_data.get('light_email_sent', False)
    })


@app.route('/test-sensor')
def test_sensor():
    """Read directly from the sensor"""
    chk = dht_sensor.readDHT11()
    
    if chk == 0:
        temp = dht_sensor.getTemperature()
        humid = dht_sensor.getHumidity()
        return jsonify({
            'success': True,
            'temperature': temp,
            'humidity': humid,
            'temperature_type': str(type(temp)),
            'humidity_type': str(type(humid))
        })
    else:
        return jsonify({
            'success': False,
            'error_code': chk,
            'error_message': 'Failed to read from sensor'
        })
    
@app.route ('/test-light')
def test_light():
    """ Get current light sensor data for testing """
    return jsonify(LM.get_sensor_data())

# Cleanup GPIO on exit
def cleanup():
    Motor.cleanup()
    LM.cleanup() 

atexit.register(cleanup)

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        cleanup()  # Make sure cleanup runs on keyboard interrupt
        exit()
