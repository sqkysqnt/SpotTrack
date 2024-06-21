# SPEC-001: Trilateration System Data Structure

## Background

This documentation outlines the data structures used in the trilateration system for processing and calculating positions of beacons based on distances from anchors.

## Requirements

- Process messages from various queues in RabbitMQ.
- Calibrate anchor positions based on calibration distances.
- Calculate the position of beacons using trilateration.
- Log and publish the calculated positions.
- Ensure the system can switch between different modes: setup, calibration, and show.

## Data Structures

### Messages

The system processes several types of messages. Each message type has a specific structure and purpose.

#### Anchor/Beacon Distance Message

{
    "type": "anchor_beacon_distance",
    "timestamp": "2024-06-20T23:33:54.555278Z",
    "anchor_id": "anchor2",
    "beacon_id": "beacon_001",
    "distance": 9.317551410672541
}
type: The type of the message, indicating this is an anchor/beacon distance message.
timestamp: The timestamp when the distance was recorded.
anchor_id: The unique identifier for the anchor.
beacon_id: The unique identifier for the beacon.
distance: The measured distance between the anchor and the beacon.

####Anchor/Anchor Distance Message


{
    "type": "anchor_anchor_distance",
    "timestamp": "2024-06-20T23:33:54.555278Z",
    "anchor_id_1": "anchor1",
    "anchor_id_2": "anchor2",
    "distance": 2.317551410672541
}
type: The type of the message, indicating this is an anchor/anchor distance message.
timestamp: The timestamp when the distance was recorded.
anchor_id_1: The unique identifier for the first anchor.
anchor_id_2: The unique identifier for the second anchor.
distance: The measured distance between the two anchors.


####Anchor Aware Message


{
    "type": "anchor_aware",
    "timestamp": "2024-06-20T23:33:54.555278Z",
    "anchor_id": "anchor1"
}
type: The type of the message, indicating this is an anchor aware message.
timestamp: The timestamp when the anchor became aware.
anchor_id: The unique identifier for the anchor.

####Calculated Position Message

{
    "type": "calculated_position",
    "timestamp": "2024-06-20T23:35:25.098456Z",
    "beacon_id": "beacon_001",
    "position": {
        "x": 3.3005320073297106,
        "y": 1.6928521208073555,
        "z": 7.3197117697099685
    },
    "accuracy": 0.9242440455941489
}
type: The type of the message, indicating this is a calculated position message.
timestamp: The timestamp when the position was calculated.
beacon_id: The unique identifier for the beacon.
position: The calculated position of the beacon in 3D space, including x, y, and z coordinates.
accuracy: The accuracy of the calculated position.

####Camera Position Message

{
    "type": "camera_position",
    "camera_id": "camera_1",
    "timestamp": "2024-06-20T23:35:25.107074Z",
    "positions": [
        {
            "beacon_id": "beacon_001",
            "position": {
                "x": 0.6710715480248464,
                "y": 1.1432246830025128,
                "z": 3.163616670785215
            },
            "confidence": 0.9607110657689085
        }
    ]
}
type: The type of the message, indicating this is a camera position message.
camera_id: The unique identifier for the camera.
timestamp: The timestamp when the positions were recorded.
positions: A list of detected positions by the camera, each including:
beacon_id: The unique identifier for the beacon.
position: The detected position of the beacon in 3D space, including x, y, and z coordinates.
confidence: The confidence level of the detected position.

###Usage

####Processing Messages
The consume_messages.py script processes incoming messages from RabbitMQ. It handles different types of messages and processes them accordingly:

1. Anchor/Beacon Distance: Updates the distance measurements between anchors and beacons.
2. Anchor/Anchor Distance: Updates the distance measurements between anchors for calibration.
3. Anchor Aware: Logs awareness of an anchor.
4. Calculated Position: Logs and publishes the calculated position of a beacon.
5. Camera Position: Logs and publishes the positions detected by cameras.


####Calibration and Trilateration
The trilateration.py script is responsible for performing trilateration calculations to determine the position of beacons based on the distances from multiple anchors. The script uses the following steps:

1. Calibration: Uses known distances to calculate the positions of the anchors.
2. Trilateration: Uses the distances from multiple anchors to a beacon to calculate the beacon's position in 3D space.


import numpy as np

##### Function to perform trilateration
def trilateration(anchor_coords, distances):
    A = 2 * (anchor_coords[1:] - anchor_coords[0])
    b = distances[0]**2 - distances[1:]**2 + np.sum(anchor_coords[1:]**2, axis=1) - np.sum(anchor_coords[0]**2)
    
    # Solve the linear system A * x = b for x
    position = np.linalg.lstsq(A, b, rcond=None)[0]
    
    return position

##### Calibration function to calculate anchor positions based on calibration beacon
def calibrate_anchors(distances_to_calibration_beacon):
    calibration_beacon_coords = np.array([0, 0, 0])
    anchor_coords = [calibration_beacon_coords]
    
    for i in range(1, 4):
        base_coords = [calibration_beacon_coords, np.zeros(3)]
        base_coords[1][i - 1] = 1
        anchor_coords.append(trilateration(np.array(base_coords), distances_to_calibration_beacon[[0, i]]))
    
    return np.array(anchor_coords)


####Logging and Publishing
All processed and calculated data are logged for debugging and monitoring purposes. Additionally, calculated positions are published back to RabbitMQ for further processing or usage by other systems.

###Modes

The system can operate in different modes based on the value of the MODE environment variable:

setup: Initializes the system and prepares it for calibration.
calibration: Performs calibration to determine the positions of the anchors.
show: Processes and logs data in real-time for monitoring and analysis.



Anchor Exists Packet
The anchor_exists packet is sent by an anchor to indicate its presence in the system. This packet contains essential information about the anchor, such as its unique identifier, firmware version, MAC address, and status.

Packet Structure

json
Copy code
{
    "type": "anchor_exists",
    "timestamp": "2024-06-20T23:33:54.555278Z",
    "anchor_id": "anchor1",
    "firmware_version": "1.0.0",
    "mac_address": "00:1B:44:11:3A:B7",
    "status": "active"
}
Field Descriptions

type: The type of the message, which is anchor_exists in this case.
timestamp: The timestamp when the packet was generated.
anchor_id: The unique identifier for the anchor.
firmware_version: The version of the firmware running on the anchor.
mac_address: The MAC address of the anchor.
status: The status of the anchor (e.g., active, inactive).
