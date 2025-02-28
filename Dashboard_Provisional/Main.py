import asyncio
from flask import Flask, jsonify, render_template

#import LED
#import TempHum
#import Profile_Manager
#import MQTT_Manager

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp-hum')
def get_TH_data():
    return jsonify(TempHum.get_sensor_data())

@app.route('/toggle-off')
def fan_off():
    #TempHum.toggle_fan("OFF")
    return False

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        #TempHum.sensorOff()
        exit()