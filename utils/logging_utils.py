import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import os
import asyncio
import json

logger = logging.getLogger("utils.logging_utils")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'system.log', maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

active_websockets = []
log_queue = asyncio.Queue()

def initialize_db():
    if not os.path.exists('logs.db'):
        conn = sqlite3.connect('logs.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    # Connect to the database and create the anchor_points table if it doesn't exist
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS anchor_points (
        id TEXT PRIMARY KEY,
        x_coordinate REAL NOT NULL,
        y_coordinate REAL NOT NULL,
        z_coordinate REAL NOT NULL,
        status TEXT NOT NULL,
        last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        firmware_version TEXT,
        user_defined_name TEXT,
        user_defined_location TEXT,
        webpage_x INTEGER,
        webpage_y INTEGER,
        mac_address TEXT,
        ip_address TEXT
    )
    ''')
    conn.commit()
    conn.close()

def log_to_db(timestamp, level, message):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)", (timestamp, level, message))
    conn.commit()
    conn.close()

    # Send log to all connected WebSocket clients
    log_entry = f"{timestamp} [{level}]: {message}"
    for websocket in active_websockets:
        asyncio.create_task(websocket.send_text(log_entry))

async def process_log_queue():
    while True:
        log_entry = await log_queue.get()
        for websocket in active_websockets:
            await websocket.send_text(log_entry)

def fetch_logs():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, level, message FROM logs ORDER BY timestamp DESC LIMIT 100")
    logs = cursor.fetchall()
    conn.close()
    return logs

class DBHandler(logging.Handler):
    def emit(self, record):
        timestamp = self.format(record).split(' - ')[0]
        level = record.levelname
        message = record.getMessage()
        log_to_db(timestamp, level, message)

def insert_anchor_point(message):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    anchor_data = json.loads(message)
    c.execute('''
        INSERT INTO anchor_points (id, x_coordinate, y_coordinate, z_coordinate, status, last_updated, firmware_version, user_defined_name, user_defined_location, webpage_x, webpage_y, mac_address, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
        status=excluded.status,
        last_updated=excluded.last_updated,
        firmware_version=excluded.firmware_version,
        user_defined_name=excluded.user_defined_name,
        user_defined_location=excluded.user_defined_location,
        webpage_x=excluded.webpage_x,
        webpage_y=excluded.webpage_y,
        mac_address=excluded.mac_address,
        ip_address=excluded.ip_address
    ''', (
        anchor_data['anchor_id'],
        anchor_data.get('x_coordinate', 0.0),
        anchor_data.get('y_coordinate', 0.0),
        anchor_data.get('z_coordinate', 0.0),
        anchor_data['status'],
        anchor_data['timestamp'],
        anchor_data['firmware_version'],
        anchor_data.get('user_defined_name', ''),
        anchor_data.get('user_defined_location', ''),
        anchor_data.get('webpage_x', 0),
        anchor_data.get('webpage_y', 0),
        anchor_data['mac_address'],
        anchor_data['ip_address']
    ))
    conn.commit()
    conn.close()

def update_anchor_point(id, x, y, z, status, firmware_version, user_defined_name, user_defined_location, webpage_x, webpage_y, mac_address, ip_address):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('''
    UPDATE anchor_points
    SET x_coordinate = ?, y_coordinate = ?, z_coordinate = ?, status = ?, firmware_version = ?, user_defined_name = ?, user_defined_location = ?, webpage_x = ?, webpage_y = ?, mac_address = ?, ip_address = ?, last_updated = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (x, y, z, status, firmware_version, user_defined_name, user_defined_location, webpage_x, webpage_y, mac_address, ip_address, id))
    conn.commit()
    conn.close()

def get_anchor_points():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, x_coordinate, y_coordinate, z_coordinate, status, last_updated, firmware_version, user_defined_name, user_defined_location, webpage_x, webpage_y, mac_address, ip_address FROM anchor_points")
    anchor_points = cursor.fetchall()
    conn.close()
    return anchor_points

    

db_handler = DBHandler()
db_handler.setFormatter(formatter)
logger.addHandler(db_handler)



