import pika
import json
from datetime import datetime

def generate_anchor_exists_packet(anchor_id, firmware_version, mac_address, status):
    packet = {
        "type": "anchor_exists",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "anchor_id": anchor_id,
        "firmware_version": firmware_version,
        "mac_address": mac_address,
        "status": status
    }
    return packet

def publish_message(rabbitmq_host, queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)  # Ensure the queue is declared as durable
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ))
    connection.close()

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
queue_name = 'anchor_exists_queue'

# Generate and send 4 test anchor packets
anchors = [
    {"anchor_id": "anchor1", "firmware_version": "1.0.0", "mac_address": "00:1B:44:11:3A:B7", "status": "active"},
    {"anchor_id": "anchor2", "firmware_version": "1.0.0", "mac_address": "00:1B:44:11:3A:B8", "status": "active"},
    {"anchor_id": "anchor3", "firmware_version": "1.0.0", "mac_address": "00:1B:44:11:3A:B9", "status": "active"},
    {"anchor_id": "anchor4", "firmware_version": "1.0.0", "mac_address": "00:1B:44:11:3A:BA", "status": "active"}
]

for anchor in anchors:
    packet = generate_anchor_exists_packet(
        anchor_id=anchor["anchor_id"],
        firmware_version=anchor["firmware_version"],
        mac_address=anchor["mac_address"],
        status=anchor["status"]
    )
    publish_message(rabbitmq_host, queue_name, packet)
    print(f"Sent packet: {packet}")
