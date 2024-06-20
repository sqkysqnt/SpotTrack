import pika
import json
import logging
import numpy as np
import trilateration  # Assuming trilateration.py is in the same directory or installed as a module

# Initialize dictionaries to hold distances and anchor positions
distances = {}
calibration_distances = {}
anchor_positions = {}
mode = "error"  # Default mode to error if not set properly

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def set_mode(new_mode):
    global mode
    if new_mode in ["setup", "calibration", "show"]:
        mode = new_mode
    else:
        mode = "error"
    logging.info(f"Mode set to: {mode}")

def process_anchor_beacon_distance(message, channel):
    global calibration_distances, anchor_positions, distances
    logging.info(f"Processing anchor/beacon distance: {message}")

    beacon_id = message["beacon_id"]
    anchor_id = message["anchor_id"]
    distance = message["distance"]

    if mode == "calibration":
        # Collect distances for calibration
        calibration_distances[anchor_id] = distance
        logging.debug(f"Calibration distances: {calibration_distances}")
        if len(calibration_distances) == 4:
            # Perform calibration
            logging.debug("Performing calibration")
            anchor_positions = trilateration.calibrate_anchors(np.array(list(calibration_distances.values())))
            logging.info(f"Calibrated anchor positions: {anchor_positions}")
            calibration_distances = {}  # Reset calibration distances for the next calibration cycle
    elif mode == "show":
        # Collect distances for show mode
        if beacon_id not in distances:
            distances[beacon_id] = {}
        distances[beacon_id][anchor_id] = distance
        logging.debug(f"Distances for beacon {beacon_id}: {distances[beacon_id]}")
        if len(distances[beacon_id]) == 4:
            # Check if anchor positions are populated
            if len(anchor_positions) == 4:
                # Perform trilateration
                logging.debug(f"Triggering trilateration with anchor positions: {anchor_positions}")
                anchor_coords = np.array([anchor_positions[i] for i in range(4)])
                logging.debug(f"Anchor coordinates: {anchor_coords}")
                beacon_position = trilateration.trilateration(anchor_coords, np.array(list(distances[beacon_id].values())))
                logging.info(f"Calculated position for beacon {beacon_id}: {beacon_position}")
                
                # Publish calculated position back to the queue
                calculated_position_message = {
                    "type": "calculated_position",
                    "timestamp": message["timestamp"],
                    "beacon_id": beacon_id,
                    "position": beacon_position.tolist(),
                    "accuracy": 0.99  # Placeholder accuracy value
                }
                channel.basic_publish(
                    exchange='',
                    routing_key='calculated_positions_queue',
                    body=json.dumps(calculated_position_message)
                )
                logging.debug(f"Published calculated position for beacon {beacon_id}: {calculated_position_message}")
                
                distances[beacon_id] = {}  # Reset distances for next calculation
            else:
                logging.warning("Anchor positions are not fully calibrated")

def process_anchor_anchor_distance(message):
    if mode == "calibration":
        logging.info(f"Processing anchor/anchor distance: {message}")

def process_anchor_aware(message):
    if mode == "calibration":
        logging.info(f"Processing anchor aware: {message}")

def process_camera_position(message):
    if mode == "show":
        logging.info(f"Processing camera position: {message}")

def process_calculated_position(message):
    if mode == "show":
        logging.info(f"Processing calculated position: {message}")

def process_system_setup(message):
    if mode == "setup":
        logging.info(f"Processing system setup: {message}")
        # Handle setup logic here

# Connect to RabbitMQ and consume messages
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Callback functions for each queue
    def callback_anchor_beacon_distance(ch, method, properties, body):
        message = json.loads(body)
        process_anchor_beacon_distance(message, channel)

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

    def callback_system_setup(ch, method, properties, body):
        message = json.loads(body)
        process_system_setup(message)

    # Set up consumers
    channel.basic_consume(queue='anchor_beacon_distance_queue', on_message_callback=callback_anchor_beacon_distance, auto_ack=True)
    channel.basic_consume(queue='anchor_anchor_distance_queue', on_message_callback=callback_anchor_anchor_distance, auto_ack=True)
    channel.basic_consume(queue='anchor_aware_queue', on_message_callback=callback_anchor_aware, auto_ack=True)
    channel.basic_consume(queue='camera_position_queue', on_message_callback=callback_camera_position, auto_ack=True)
    channel.basic_consume(queue='calculated_positions_queue', on_message_callback=callback_calculated_position, auto_ack=True)
    channel.basic_consume(queue='system_setup_queue', on_message_callback=callback_system_setup, auto_ack=True)

    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    # Example: set initial mode to 'setup'
    set_mode("show")
    consume_messages()
