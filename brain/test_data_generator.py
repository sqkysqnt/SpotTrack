import pika
import json
import numpy as np
import random
from datetime import datetime

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'

# Anchors coordinates (example values)
anchors = {
    "anchor1": (0, 0, 0),
    "anchor2": (10, 0, 0),
    "anchor3": (0, 10, 0),
    "anchor4": (10, 10, 0)
}

# Function to simulate a beacon's position
def simulate_beacon_position():
    return np.random.uniform(0, 10, size=3)

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt(np.sum((np.array(point1) - np.array(point2)) ** 2))

# Function to publish a message to RabbitMQ
def publish_message(exchange, routing_key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message))
    connection.close()

# Function to generate and send anchor/beacon distance messages
def generate_anchor_beacon_distance(beacon_position):
    for anchor_id, anchor_pos in anchors.items():
        distance = calculate_distance(anchor_pos, beacon_position)
        message = {
            "type": "anchor_beacon_distance",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "anchor_id": anchor_id,
            "beacon_id": "beacon_001",
            "distance": distance
        }
        publish_message('tracking_exchange', 'anchor_beacon_distance', message)

# Function to generate and send anchor/anchor distance messages
def generate_anchor_anchor_distance():
    anchor_ids = list(anchors.keys())
    anchor1, anchor2 = random.sample(anchor_ids, 2)
    distance = calculate_distance(anchors[anchor1], anchors[anchor2])
    message = {
        "type": "anchor_anchor_distance",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "anchor_id": anchor1,
        "other_anchor_id": anchor2,
        "distance": distance
    }
    publish_message('tracking_exchange', 'anchor_anchor_distance', message)

# Function to generate and send anchor aware messages
def generate_anchor_aware():
    anchor_ids = list(anchors.keys())
    target_anchor, neighbor_anchor = random.sample(anchor_ids, 2)
    message = {
        "type": "anchor_aware",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "target_anchor_id": target_anchor,
        "neighbor_anchor_id": neighbor_anchor
    }
    publish_message('tracking_exchange', 'anchor_aware', message)

# Function to generate and send camera position messages
def generate_camera_positions(beacon_position):
    for camera_id in ["camera_1", "camera_2"]:
        message = {
            "type": "camera_position",
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "positions": [
                {
                    "beacon_id": "beacon_001",
                    "position": {
                        "x": beacon_position[0],
                        "y": beacon_position[1],
                        "z": beacon_position[2]
                    },
                    "confidence": np.random.uniform(0.8, 1.0)
                }
            ]
        }
        publish_message('tracking_exchange', 'camera_position', message)

# Function to generate and send calculated position messages
def generate_calculated_position(beacon_position):
    message = {
        "type": "calculated_position",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "beacon_id": "beacon_001",
        "position": {
            "x": beacon_position[0],
            "y": beacon_position[1],
            "z": beacon_position[2]
        },
        "accuracy": np.random.uniform(0.8, 1.0)
    }
    publish_message('tracking_exchange', 'calculated_position', message)

# Main loop to generate and send test data
def main():
    while True:
        # Simulate a beacon's position
        beacon_position = simulate_beacon_position()
        
        # Randomly select a message type to generate
        message_type = random.choice([
            'anchor_beacon_distance',
            'anchor_anchor_distance',
            'anchor_aware',
            'camera_position',
            'calculated_position'
        ])
        
        if message_type == 'anchor_beacon_distance':
            generate_anchor_beacon_distance(beacon_position)
        elif message_type == 'anchor_anchor_distance':
            generate_anchor_anchor_distance()
        elif message_type == 'anchor_aware':
            generate_anchor_aware()
        elif message_type == 'camera_position':
            generate_camera_positions(beacon_position)
        elif message_type == 'calculated_position':
            generate_calculated_position(beacon_position)

if __name__ == "__main__":
    main()
