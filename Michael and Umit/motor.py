import RPi.GPIO as GPIO
import time
import math
import paho.mqtt.client as mqtt
import datetime
import ssl
import json

OPEN_TIME = 6
CLOSE_TIME = 20
GATE_OPEN_CLOSE_SECONDS = 2

OPEN = True
FIRE_DETECTED = False
#CHICKENS_MAGNETOMETER_VALUE = 0
CHICKENS_IN_BED = True

#mqtt data
host          = "node02.myqtthub.com"
port          = 1883
clean_session = True
client_id     = "motor"
user_name     = "bravogate@yopmail.com"
password      = "8sLBIaF9-m5OvAlEA"

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))

    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
    client.subscribe("aberdeen/animalhouse/chicken/1/fire")
    client.subscribe("aberdeen/animalhouse/chicken/1/inbed")
    client.subscribe("aberdeen/animalhouse/chicken/1/test")

    if rc == 0:
        client.connected_flag = True
        print ("connected OK")
        return

    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # Handle error here
    sys.exit (-1)

def on_message(client, userdata, msg):
    jsonStr = str(msg.payload.decode("UTF-8"))
    print("MESSEGE RECEIVED")
    print(jsonStr)
    print()
    global FIRE_DETECTED
    global CHICKENS_IN_BED
    
    message = json.loads(jsonStr)
    
    if message["property"] == "fire":
        if message["hasResult"]["value"] == "True":
            FIRE_DETECTED = True
            print("fire")
        else :
            FIRE_DETECTED = False
            print("no fire")
    elif message["property"] == "animal in bed":
        print(message["hasResult"]["value"]);
        values = message["hasResult"]["value"];
        CHICKENS_IN_BED = True;
        
        #check all chickens in bed
        for i in values:
            if i == "False":
                CHICKENS_IN_BED = False
                return
    else :
        print(message["hasResult"]["value"])

#testing mqtt
def publish_test_status():
    print("...Publishing Test Status...")
    observation = {"featureOfInterest": "chicken house 1", "property": "Test", "resultTime":str(datetime.datetime.now()), "hasResult":{"value":"Test"}}
    print(json.dumps(observation)) 
    client.publish("aberdeen/animalhouse/chicken/1/test", json.dumps(observation))
    print()

# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect
client.on_message = on_message

# Configure TLS connection
client.tls_set (cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set (False)
port = 8883

# Connect using secure MQTT with keepalive 60
client.connect (host, port, keepalive = 60)
client.loop_start()

client.connected_flag = False

while not client.connected_flag:
    client.loop()
    time.sleep (1)

#motor
Motor1A = 17
Motor1B = 27
Motor1E = 22

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Motor1A, GPIO.OUT)
    GPIO.setup(Motor1B, GPIO.OUT)
    GPIO.setup(Motor1E, GPIO.OUT)

#test method
def loop():
    #forwards
    open()
    time.sleep(2)

    #backwards
    close()
    time.sleep(2)

def open():
    print("opening")
    
    global OPEN

    GPIO.output(Motor1A, GPIO.HIGH)
    GPIO.output(Motor1B, GPIO.LOW)
    GPIO.output(Motor1E, GPIO.HIGH)

    time.sleep(GATE_OPEN_CLOSE_SECONDS)

    GPIO.output(Motor1E, GPIO.LOW)

    OPEN = True
    

def close():
    print("closing")

    global OPEN
    
    GPIO.output(Motor1A, GPIO.LOW)
    GPIO.output(Motor1B, GPIO.HIGH)
    GPIO.output(Motor1E, GPIO.HIGH)

    time.sleep(GATE_OPEN_CLOSE_SECONDS)

    GPIO.output(Motor1E, GPIO.LOW)

    OPEN = False

def destroy():
    GPIO.cleanup()

# Check MQTT every mqtt_check_time seconds
mqtt_check_time = 10

if __name__ == '__main__':
    setup()
    try:
        while True :
            #publish_test_status()
            print("Checking sensor status...")
            print("Chickens in bed: " + str(CHICKENS_IN_BED))
            print("Fire detected: " + str(FIRE_DETECTED))
            print("Open: " + str(OPEN))
            print()
            if (((datetime.datetime.now().hour >= OPEN_TIME) and (datetime.datetime.now().hour < CLOSE_TIME)) or (FIRE_DETECTED == True)) and OPEN == False :
                open()
            elif (((((datetime.datetime.now().hour >= CLOSE_TIME) and (datetime.datetime.now().hour <= 24)) or ((datetime.datetime.now().hour >= 0) and (datetime.datetime.now().hour < OPEN_TIME))) and CHICKENS_IN_BED == True) and (FIRE_DETECTED == False)) and OPEN == True :
                close()
            time.sleep(mqtt_check_time)
    except KeyboardInterrupt:
        destroy()
        client.disconnect()
        client.loop_stop()
