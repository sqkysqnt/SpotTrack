import subprocess
import signal
import sys
import os
import time
import threading
from utils.mqtt_utils import mqtt_client, get_ip_address, start_mqtt_client, configure_rabbitmq
from utils.logging_utils import logger, initialize_db

def check_rabbitmq():
    result = subprocess.run(['systemctl', 'is-active', '--quiet', 'rabbitmq-server'])
    if result.returncode != 0:
        print("RabbitMQ server is not running. Attempting to start it...")
        result = subprocess.run(['sudo', 'systemctl', 'start', 'rabbitmq-server'])
        if result.returncode != 0:
            print("Failed to start RabbitMQ server. Attempting to configure it...")
            configure_rabbitmq()  # Attempt to fix the configuration and restart
            result = subprocess.run(['sudo', 'systemctl', 'start', 'rabbitmq-server'])
            if result.returncode != 0:
                print("Failed to start RabbitMQ server after configuration attempt. Exiting.")
                sys.exit(1)
            else:
                start_mqtt_client()
                print("RabbitMQ server started successfully after configuration attempt.")
    else:
        print("RabbitMQ server is running.")

def start_web_interface():
    # Get the full path to the python3 interpreter
    python_interpreter = os.path.join(os.getcwd(), 'env', 'bin', 'python3')
    process = subprocess.Popen([python_interpreter, 'web_interface.py'])
    return process

def stop_web_interface(process):
    process.terminate()
    process.wait()
    print("Web interface stopped successfully.")

def signal_handler(sig, frame):
    stop_web_interface(web_interface_process)
    mqtt_client.loop_stop()
    sys.exit(0)

def monitor_ip_changes():
    current_ip = get_ip_address()
    while True:
        time.sleep(10)  # Check every 10 seconds
        new_ip = get_ip_address()
        if new_ip != current_ip:
            logger.info(f"IP address changed from {current_ip} to {new_ip}. Reconnecting MQTT client.")
            mqtt_client.disconnect()
            start_mqtt_client()
            current_ip = new_ip

if __name__ == "__main__":
    initialize_db()
    check_rabbitmq()
    web_interface_process = start_web_interface()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    threading.Thread(target=monitor_ip_changes).start()
    print("Web interface is running. Press Ctrl+C to stop.")
    try:
        web_interface_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    print("Web interface process has exited. Stopping the program.")
    stop_web_interface(web_interface_process)
    mqtt_client.loop_stop()
    sys.exit(0)
