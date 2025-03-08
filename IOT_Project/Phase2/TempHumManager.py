import time
import Freenove_DHT as DHT
import MotorFunction as Motor
import EmailManager as EM


email_sent = False
fan_on = False

def disableFan():
    global fan_on
    fan_on = False

def get_sensor_data():

    # DHT block to get the data for the temperature and humidity.

    # Checks if the temperature passes the threshold or not. If yes, send the email.
    if (temperature_data > 20 and not email_sent and not fan_on):
        email_sent = True
        msg = "The temperature has breached the threshold. Would you like to turn the fan on?"
        EM.email_notification(msg)

    # Checks if the email was sent. If sent, the fan/motor isn't enabled and the keyword's inside the mail content, turns the fan on.
    if (email_sent and not fan_on):

    # Returns the DHT data.

    return {
            'temperature': temperature_data,
            'humidity': humidity_data,
            'fan': fan_on
            }