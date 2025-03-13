from flask import Flask, jsonify, render_template
import atexit
import TempHumManager as THM
import MotorFunction as Motor

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

# Cleanup GPIO on exit
atexit.register(Motor.cleanup)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        exit()