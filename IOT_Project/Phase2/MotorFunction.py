import RPi.GPIO as GPIO
import THM2 as THM
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Motor1 = 17 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 22 # Input Pin


GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

def toggle(state):

    if state:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.HIGH)
    else:
        THM.disableFan()
        GPIO.output(Motor1,GPIO.LOW)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.LOW)

    #return jsonify({'success': True, 'fan': fan_on})

def cleanup():
    GPIO.cleanup()