import paho.mqtt.client as mqtt
import json

# Function to handle incoming messages
def on_message(client, userdata, msg):
    device_info = json.loads(msg.payload)
    print(f"Received message from {device_info['device_id']}: {device_info}")

    # Create the configuration message to send to the device
    config_message = {
        "device_id": device_info['device_id'],
        "network_config": {
            "target_ssid": "PerformanceNetwork",
            "target_password": "performance_password"
        },
        "operational_params": {
            "mode": "calibration",
            "calibration_data": None
        }
    }

    # Publish the configuration message to the device-specific topic
    client.publish(f"stage_tracking/config/{device_info['device_id']}", json.dumps(config_message))

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("stage_tracking/device_info")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    # Set up MQTT client authentication
    client.username_pw_set("stagetrack", "trackstage")
    # Connect to the MQTT broker (assuming it's running locally)
    client.connect("localhost", 1883, 60)

    # Start the loop to process callbacks and handle incoming messages
    client.loop_forever()

if __name__ == "__main__":
    main()
