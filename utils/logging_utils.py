import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import os

# Initialize logger
logger = logging.getLogger("utils.logging_utils")
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler(
    'system.log', maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def initialize_db():
    if not os.path.exists('logs.db'):
        conn = sqlite3.connect('logs.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            log_message TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

def log_to_db(message):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    timestamp = message.split(' - ')[0]
    c.execute("INSERT INTO logs (timestamp, log_message) VALUES (?, ?)", (timestamp, message))
    conn.commit()
    conn.close()

class DBHandler(logging.Handler):
    def emit(self, record):
        log_to_db(self.format(record))

# Add the custom database handler to the logger
db_handler = DBHandler()
db_handler.setFormatter(formatter)
logger.addHandler(db_handler)
