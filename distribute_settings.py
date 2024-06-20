import paho.mqtt.client as mqtt
import json

# Define the settings to be distributed
settings = {
    "ssid": "PerformanceNetwork",
    "password": "performance_password",
    "mode": "setup"
}

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish("stage_tracking/settings", json.dumps(settings))

def main():
    client = mqtt.Client()
    client.on_connect = on_connect

    # Connect to the MQTT broker (assuming it's running locally)
    client.connect("localhost", 1883, 60)

    # Start the loop to process callbacks and publish settings
    client.loop_forever()

if __name__ == "__main__":
    main()
