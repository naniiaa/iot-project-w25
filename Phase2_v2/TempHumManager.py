import time
import Freenove_DHT as DHT
import MotorFunction as Motor
import EmailManager as EM
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('temp_hum_manager')

email_sent = False
fan_on = False
last_email_time = 0

# Initialize the DHT sensor
DHT_PIN = 23

dht_sensor = DHT.DHT(DHT_PIN)  # Assuming the sensor is connected to GPIO pin 17

def disableFan():
    global fan_on
    fan_on = False
    Motor.toggle(False)  # Turn off the fan
    logger.info("FAN TURNED OFF")

def enableFan():
    global fan_on
    fan_on = True
    Motor.toggle(True) # Turn on the fan
    logger.info("FAN TURNED ON")

def get_sensor_data():
    global email_sent, fan_on, last_email_time

    # Read temperature and humidity data from the DHT sensor
    chk = dht_sensor.readDHT11()

    if chk == 0:  # If the sensor reading is successful
        temperature_data = dht_sensor.getTemperature()
        humidity_data = dht_sensor.getHumidity()

        logger.info(f"Temperature: {temperature_data} )C, Humidity: {humidity_data}%")

        current_time = time.time()
  
        # Check if temperature exceeds 24°C and email hasn't been sent yet
        if temperature_data > 20 and not email_sent:
            
            # Prepare and send email
            msg = f"The current temperature is {temperature_data} degree celsius. Would you like to turn on the fan?"
            email_result = EM.email_notification(msg)

            if email_result:
                email_sent = True
                last_email_time = current_time
                logger.info("Temp alert email sent succesfully!")
            else:
                logger.error("Failed to send temp alert email")


        # Check if the user replied YES
        if email_sent:
            reply = EM.check_user_reply()
            logger.info(f"User replied: {reply}, Fan is on: {fan_on}")
            if reply == "YES" and not fan_on:
                enableFan()
            elif reply == "NO" and fan_on:
                disableFan()


        return {
            'temperature': float(temperature_data),  
            'humidity': float(humidity_data),  
            'fan': fan_on,
            'email_sent': email_sent 
        }
    else:
        logger.warning(f"DHT sensor reading failed w/ code: {chk}")
        return {
             'temperature': None,  
            'humidity': None,
            'fan': fan_on,
            'email_sent': email_sent,
        }

