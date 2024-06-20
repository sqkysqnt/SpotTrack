import pika
import json
from datetime import datetime
import time
import math

# Placeholder for your processing functions
def process_anchor_beacon_distance(message):
    # Process anchor/beacon distance message
    print(f"Processing anchor/beacon distance: {message}")

def process_anchor_anchor_distance(message):
    # Process anchor/anchor distance message
    print(f"Processing anchor/anchor distance: {message}")

def process_anchor_aware(message):
    # Process anchor aware message
    print(f"Processing anchor aware: {message}")

def process_camera_position(message):
    # Process camera position message
    print(f"Processing camera position: {message}")

def process_calculated_position(message):
    # Process calculated position message
    print(f"Processing calculated position: {message}")

# Connect to RabbitMQ and consume messages
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Callback functions for each queue
    def callback_anchor_beacon_distance(ch, method, properties, body):
        message = json.loads(body)
        process_anchor_beacon_distance(message)

    def callback_anchor_anchor_distance(ch, method, properties, body):
        message = json.loads(body)
        process_anchor_anchor_distance(message)

    def callback_anchor_aware(ch, method, properties, body):
        message = json.loads(body)
        process_anchor_aware(message)

    def callback_camera_position(ch, method, properties, body):
        message = json.loads(body)
        process_camera_position(message)

    def callback_calculated_position(ch, method, properties, body):
        message = json.loads(body)
        process_calculated_position(message)

    # Set up consumers
    channel.basic_consume(queue='anchor_beacon_distance_queue', on_message_callback=callback_anchor_beacon_distance, auto_ack=True)
    channel.basic_consume(queue='anchor_anchor_distance_queue', on_message_callback=callback_anchor_anchor_distance, auto_ack=True)
    channel.basic_consume(queue='anchor_aware_queue', on_message_callback=callback_anchor_aware, auto_ack=True)
    channel.basic_consume(queue='camera_position_queue', on_message_callback=callback_camera_position, auto_ack=True)
    channel.basic_consume(queue='calculated_positions_queue', on_message_callback=callback_calculated_position, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    consume_messages()
