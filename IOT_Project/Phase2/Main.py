from flask import Flask, jsonify, render_template
import atexit
import TempHumManager as THM
import MotorFunction as Motor
import Freenove_DHT as dht_sensor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp-hum')
def get_TH_data():
    return jsonify(THM.get_sensor_data())  # Grabs the DHT data and converts it into JSON

@app.route('/toggle-off')
def fan_off():
    Motor.toggle(False)
    return jsonify({"status": "Fan turned off"})

@app.route('/email-status')
def get_email_status():
    return jsonify({
        'email_sent': THM.email_sent,
        'last_email_time': THM.last_email_time if hasattr(THM, 'last_email_time') else None,
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
    
# Cleanup GPIO on exit
atexit.register(Motor.cleanup)

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=5001)
    except KeyboardInterrupt:
        exit()