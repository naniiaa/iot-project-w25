from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO

app = Flask(__name__)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)  # Switch input
GPIO.setup(27, GPIO.OUT)  # LED output

@app.route('/')
def index():
    return render_template('index.html')

#get method changes the LedStatus
@app.route('/toggle_led', methods=['GET'])
def toggle_led():
    status = request.args.get('status')

    if status == 'ON':
        GPIO.output(27, GPIO.HIGH)  # LED ON
    else:
        GPIO.output(27, GPIO.LOW)  # LED OFF
    
    return jsonify(message=f"LED turned {status}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
