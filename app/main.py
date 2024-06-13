from fastapi import FastAPI
from pydantic import BaseModel
from app.rabbitmq import setup_connection, publish_message
from app.osc import setup_client, send_message

app = FastAPI()

# RabbitMQ setup
connection, channel = setup_connection()

# OSC setup
osc_client = setup_client()

class Message(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/send_message/")
def send_message_endpoint(msg: Message):
    publish_message(channel, msg.message)
    send_message(osc_client, "/filter", msg.message)
    return {"status": "Message sent", "content": msg.message}
