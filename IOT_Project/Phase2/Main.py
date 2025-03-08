import asyncio
from flask import Flask, jsonify, render_template

#import LED
import TempHumManager as THM
import MotorFunction as Motor
#import Profile_Manager
#import MQTT_Manager

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp-hum')
def get_TH_data():
    return jsonify(THM.get_sensor_data()) # Grabs the DHT data from the TempHumManager file and converts it into json for Javascript.

@app.route('/toggle-off')
def fan_off():
    Motor.toggle(False)
    return False

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        exit()