import paho.mqtt.client as mqtt
import json
import time
import socket
import uuid

# Function to get the device's IP address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Doesn't need to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Function to get the MAC address
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                    for elements in range(0, 2*6, 2)][::-1])
    return mac

# Function to simulate getting signal strength
def get_signal_strength():
    return -40  # Placeholder value for RSSI

# Define the device information
device_info = {
    "device_id": "RPI001",
    "device_type": "raspberry_pi",
    "mac_address": get_mac_address(),
    "ip_address": get_ip_address(),
    "current_ssid": "StageTrackingSetup",
    "firmware_version": "1.0.0",
    "capabilities": ["camera"],
    "health_status": {
        "battery_level": None,
        "signal_strength": get_signal_strength()
    }
}

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish("stage_tracking/device_info", json.dumps(device_info))

def main():
    client = mqtt.Client()
    client.on_connect = on_connect

    # Connect to the MQTT broker (assuming it's running on the same network)
    client.connect("192.168.4.1", 1883, 60)

    # Start the loop to process callbacks and publish device information
    client.loop_start()

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.loop_stop()

if __name__ == "__main__":
    main()
