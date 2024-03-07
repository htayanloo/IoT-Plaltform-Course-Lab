import json
import time
import random
import paho.mqtt.client as mqtt

# Load the device configuration
with open('device_config.json', 'r') as file:
    config = json.load(file)

# Define the simulation time in seconds (1 hour = 3600 seconds)
simulation_time = 3600

# Function to simulate sensor data generation
def simulate_sensor_data(sensor, last_value):
    if sensor['type'] == 'float' or sensor['type'] == 'int':
        new_value = last_value + sensor['step']
        if new_value > sensor['maxValue'] or new_value < sensor['minValue']:
            sensor['step'] = -sensor['step']
            new_value = last_value + sensor['step']
    else:  # For binary sensors
        new_value = random.choice(sensor['values'])
    return new_value

# Function to send data to ThingsBoard
def send_data(device_name, device_config, duration):
    client = mqtt.Client()
    
    # Connect to ThingsBoard
    client.connect("192.168.3.225", 1883, 60)
    client.loop_start()

    sensor_values = {}
    for sensor in device_config['sensors']:
       
        if sensor['type'] == 'float' or sensor['type'] == 'int':
            sensor_values[sensor['name']] = random.uniform(sensor['minValue'], sensor['maxValue'])
        else:
            sensor_values[sensor['name']] = random.choice(sensor['values'])

    start_time = time.time()

    while int(time.time() - start_time) < duration:
        for sensor in device_config['sensors']:
            # Update and send sensor data based on its duration

            if (int(time.time() - start_time)) % sensor['duration'] == 0:
                sensor_values[sensor['name']] = simulate_sensor_data(sensor, sensor_values[sensor['name']])
                print("sensor data")
                client.publish('v1/devices/me/telemetry', json.dumps({sensor['name']: sensor_values[sensor['name']]}), 1)

        time.sleep(1)

# Iterate over each device in the configuration and send data
for device_name, device_config in config.items():
    send_data(device_name, device_config, simulation_time)
