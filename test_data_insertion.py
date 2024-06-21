import json
from utils.logging_utils import insert_anchor_point

test_message = {
    "type": "anchor_exists",
    "timestamp": "2024-06-20T23:33:54.555278Z",
    "anchor_id": "anchor1",
    "firmware_version": "1.0.0",
    "mac_address": "00:1B:44:11:3A:B7",
    "ip_address": "192.168.1.100",
    "status": "active"
}

insert_anchor_point(json.dumps(test_message))
