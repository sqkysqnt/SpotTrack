import paho.mqtt.client as mqtt
import threading
import json
import subprocess
import time
import traceback
from utils.logging_utils import logger
from utils.network_utils import get_ip_address

devices = {}

def configure_rabbitmq():
    try:
        rabbitmq_conf = '/etc/rabbitmq/rabbitmq.conf'
        required_settings = {
            'loopback_users.guest': 'false',
            'listeners.tcp.default': '5672',
            'mqtt.listeners.tcp.default': '1883',
            'mqtt.allow_anonymous': 'true',
        }

        with open(rabbitmq_conf, 'w') as conf:
            for key, value in required_settings.items():
                conf.write(f'{key} = {value}\n')

        logger.info("RabbitMQ configuration updated successfully.")
        
        subprocess.run(['sudo', 'systemctl', 'restart', 'rabbitmq-server'], check=True)
        logger.info("RabbitMQ service restarted successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restart RabbitMQ service: {e}. Check the configuration and logs for details.")
    except Exception as e:
        logger.error(f"Failed to configure RabbitMQ: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe("stage_tracking/device_info")
        userdata["connected"] = True
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    device_info = json.loads(msg.payload)
    device_id = device_info["device_id"]
    devices[device_id] = device_info
    userdata["messages_received"] += 1
    logger.info(f"Received info from {device_id}: {device_info}")

def on_subscribe(client, userdata, mid, granted_qos):
    logger.info(f"Subscribed to topic with QoS {granted_qos}")

def on_publish(client, userdata, mid):
    logger.info(f"Message published with mid {mid}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_publish = on_publish
mqtt_client._userdata = {"subscriptions": [], "connected": False, "messages_received": 0}

def start_mqtt_client():
    mqtt_broker_ip = get_ip_address()  # Dynamically get the IP address
    logger.info(f"Attempting to connect to MQTT broker at {mqtt_broker_ip}")
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            mqtt_client.connect(mqtt_broker_ip, 1883, 60)
            logger.info("MQTT connection initiated")
            mqtt_client.loop_start()
            break  # Exit the loop if connection is successful
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            logger.debug(traceback.format_exc())
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 1} of {max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not connect to MQTT broker.")

def run_mqtt_client():
    threading.Thread(target=start_mqtt_client).start()

def get_mqtt_broker_info():
    return {
        "broker": get_ip_address(), 
        "port": 1883, 
        "status": "Connected" if mqtt_client._userdata["connected"] else "Disconnected",
        "client_id": mqtt_client._client_id.decode() if mqtt_client._client_id else "Not connected",
        "connected": mqtt_client._userdata["connected"],
        "subscriptions": mqtt_client._userdata["subscriptions"],
        "messages_received": mqtt_client._userdata["messages_received"]
    }
