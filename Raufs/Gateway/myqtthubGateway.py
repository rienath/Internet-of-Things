import paho.mqtt.client as mqtt
import time
import ssl
import json
import requests

host          = "node02.myqtthub.com"
port          = 1883
clean_session = True
client_id     = "gateway"
user_name     = "bravogate@yopmail.com"
password      = "8sLBIaF9-m5OvAlEA"

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.

    # Subscribe to CO2 sensor readings
    client.subscribe("aberdeen/animalhouse/chicken/1/carbondioxide")
    # Subscribe to magnetometers readings
    client.subscribe("aberdeen/animalhouse/chicken/1/magnetometers")

    if rc == 0:
        client.connected_flag = True
        print ("!!!Connected!!!")
        print()

        # Publish and retain a message describing this virtual Fire Sensor
        sensor_fire = {"id":4, "name":"fire sensor", "type":"Software Fire Detector", "isHostedBy":{"location":"Aberdeen"}}
        client.publish("aberdeen/animalhouse/chicken/1/fire", json.dumps(sensor_fire), retain=True, qos=2)
        print("========FIRE DETECTOR=======")
        print(json.dumps(sensor_fire))
        print()

        # Publish and retain a message describing this virtual Animal Sensor
        sensor_chicken = {"id":5, "name":"animal sensor", "type":"Software Chicken Detector", "isHostedBy":{"location":"Aberdeen"}}
        client.publish("aberdeen/animalhouse/chicken/1/inbed", json.dumps(sensor_chicken), retain=True, qos=2)
        print("======CHICKEN DETECTOR======")
        print(json.dumps(sensor_chicken))
        print()

        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # Handle error here
    sys.exit (-1)

# When a new message is received
def on_message(client, userdata, msg):
    jsonStr = str(msg.payload.decode("UTF-8"))
    print("MESSEGE RECEIVED")
    print(jsonStr)
    print()

    observation = json.loads(jsonStr)
    time = observation["resultTime"]
    sensing = observation["property"]
    place = observation["featureOfInterest"]

    # If message is from CO2 sensor
    if sensing == "CO2 presence":
        result = observation["hasResult"]
        value = result["value"]

        # It is fire if the reading is over 4000 ppm
        fire = value > 4000

        # If fire, send notification to Pushbullet
        if fire:
            fire_notification(place)

        publish_fire_status(time, fire)

    # If message is from magnetometers
    elif sensing == "magnetic field under beds":
        result = observation["hasResult"]
        values = result["value"]

        # List where true is magnet over magnetometer
        over = []
        for i in values:
                over.append(True) if i > 80 else over.append(False)
        
        # Send a notification that animals are not sleeping
        # if any of the animals are not in the bed and it is late (9pm).
        # Since magnetometer readings are received every minute, 
        # if the time is 21:00 and we send a notification,
        # it will be sent only once.
        hours = int(time[11:13])
        minutes = int(time[14:16])

        if False in over and hours == 21 and minutes == 00:
            bed_notification(place)
        
        publish_chicken_status(time, over)

# Send a notification that there is fire
def fire_notification(place):
    # IFTTT
    r = requests.post('https://maker.ifttt.com/trigger/fire/with/key/dPwWgLf1G3f5ub9KZD-Ws', params={"value1":str(place),"value2":"none","value3":"none"})
    print('Notification regarding fire sent')
    print()

# Send a notification if chicken are not in bed at night
def bed_notification(place):
    # IFTTT
    r = requests.post('https://maker.ifttt.com/trigger/chicken_not_in_bed/with/key/dPwWgLf1G3f5ub9KZD-Ws', params={"value1":str(place),"value2":"none","value3":"none"})
    print('Notification regarding awake chicken sent')
    print()

def publish_fire_status(time, status):
    print("...Publishing Fire Status...")
    observation = {"featureOfInterest": "chicken house 1", "property": "fire", "madeBySensor":"Software Fire Sensor", "resultTime":time, "hasResult":{"value":str(status)}}
    print(json.dumps(observation)) 
    client.publish("aberdeen/animalhouse/chicken/1/fire", json.dumps(observation), qos=2)
    print()

def publish_chicken_status(time, status):
    print("...Publishing Chicken In Beds Status...")
    observation = {"featureOfInterest": "chicken house 1", "property": "animal in bed", "madeBySensor":"Software Animal Sensor", "resultTime":time, "hasResult":{"value":str(status)}}
    print(json.dumps(observation)) 
    client.publish("aberdeen/animalhouse/chicken/1/inbed", json.dumps(observation), qos=2)
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


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()


# Close connection
client.disconnect()
