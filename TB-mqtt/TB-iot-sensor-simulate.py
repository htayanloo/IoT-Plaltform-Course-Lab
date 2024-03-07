#!/usr/bin/env python3
"""
Author: Hadi Tayanloo
Email: htayanloo@gmail.com
GitHub: https://github.com/htayanloo
"""

import time
import json
import paho.mqtt.client as mqtt
import threading

# Thingsboard platform credentials
THINGSBOARD_HOST = '192.168.3.225'  # Change IP Address
ACCESS_TOKEN = 'ekzarrqhnhcc91p1xwiu'
# Actuator states dictionary
actuator_states = {"actuator1": True, "actuator2": False, "actuator3": False,'Fuel':20}

def setActuatorValue(actuator, state):
    if actuator in actuator_states:
        actuator_states[actuator] = state
        print(f"{actuator} state changed to: {state}")
        # Immediately publish the new state as telemetry
        publish_telemetry()
    else:
        print("Invalid actuator name.")

def getActuatorValue(actuator):
    if actuator in actuator_states:
        return actuator_states[actuator]
    else:
        print("Invalid actuator name.")
        return None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    client.subscribe('v1/devices/me/rpc/request/+')

def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    requestId = msg.topic.split('/')[-1]
    data = json.loads(msg.payload)
    method_parts = data['method'].split('_')
    if method_parts[0] == 'setActuatorValue':
        actuator_name = method_parts[1]
        print(f"SET actuator_name: {actuator_name} data : {data['params']}")
        setActuatorValue(actuator_name, data['params'])
        client.publish('v1/devices/me/attributes', json.dumps(actuator_states), 1)
    elif method_parts[0] == 'getActuatorValue':
        
        actuator_name = method_parts[1]
        print(f"actuator_name {actuator_name}")
        value = getActuatorValue(actuator_name)
        print(f"value {value}")
        if value is not None:
            print(f"response get value : {{actuator_name: value}}")
            if actuator_name.startswith("actu"):
                client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps({'value': value}), 1)
            else:
                client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(value), 1)

def publish_telemetry():
    client.publish('v1/devices/me/telemetry', json.dumps(actuator_states), 1)
    #print("Published telemetry: ", actuator_states)

def telemetry_loop():
    while True:
        publish_telemetry()
        time.sleep(5)  # Adjust the sleep time as needed

def user_input_handler():
    while True:
        user_input = input("Enter command (e.g., 'set actuator1 on', 'get actuator2'): ")
        parts = user_input.split()
        if len(parts) == 3 and parts[0].lower() == 'set' and parts[1] in actuator_states:
            state = parts[2].lower() == 'on'
            setActuatorValue(parts[1], state)
        elif len(parts) == 2 and parts[0].lower() == 'get' and parts[1] in actuator_states:
            value = getActuatorValue(parts[1])
            print(f"{parts[1]} state is: {'on' if value else 'off'}")
        else:
            print("Invalid command. Use 'set <actuatorName> on/off' or 'get <actuatorName>'.")

# Initialize and configure the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

# Start the non-blocking loop to handle MQTT messages
client.loop_start()

# Start the telemetry publishing in a separate thread
telemetry_thread = threading.Thread(target=telemetry_loop)
telemetry_thread.daemon = True
telemetry_thread.start()

# Start the user input handler in the main thread
try:
    user_input_handler()
except KeyboardInterrupt:
    print("Program interrupted by the user. Exiting...")
finally:
    client.disconnect()
    client.loop_stop()
