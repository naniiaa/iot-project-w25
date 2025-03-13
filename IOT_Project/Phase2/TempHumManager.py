import time
import Freenove_DHT as DHT
import MotorFunction as Motor
import EmailManager as EM

email_sent = False
fan_on = False

# Initialize the DHT sensor
dht_sensor = DHT.DHT(18)  # Assuming the sensor is connected to GPIO pin 17

def disableFan():
    global fan_on
    fan_on = False
    Motor.toggle(False)  # Turn off the fan

def get_sensor_data():
    global email_sent, fan_on

    # Read temperature and humidity data from the DHT sensor
    chk = dht_sensor.readDHT11()
    if chk == 0:  # If the sensor reading is successful
        temperature_data = dht_sensor.getTemperature()
        humidity_data = dht_sensor.getHumidity()

        # Check if temperature exceeds 24°C and email hasn't been sent yet
        if temperature_data > 24 and not email_sent:
            email_sent = True
            msg = f"The current temperature is {temperature_data}°C. Would you like to turn on the fan?"
            EM.email_notification(msg)

        # Check if the user replied YES
        if email_sent and EM.check_user_reply() == "YES" and not fan_on:
            fan_on = True
            Motor.toggle(True)  # Turn on the fan

        return {
            'temperature': temperature_data,
            'humidity': humidity_data,
            'fan': fan_on
        }
    else:
        return {
            'temperature': None,
            'humidity': None,
            'fan': fan_on
        }