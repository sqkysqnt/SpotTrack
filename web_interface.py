from fastapi import FastAPI, WebSocket, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uvicorn
import json
import subprocess
import os
import socket
import asyncio
from utils.mqtt_utils import mqtt_client, start_mqtt_client
from utils.logging_utils import logger
from utils.network_utils import configure_wireless_router, get_ip_address, backup_network_config

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class DeviceConfig(BaseModel):
    device_id: str
    ssid: str
    password: str

devices = {}

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mqtt_info")
async def get_mqtt_info():
    broker_info = {
        "broker": get_ip_address(),
        "port": 1883,
        "status": "Connected" if mqtt_client._userdata["connected"] else "Disconnected"
    }
    client_info = {
        "client_id": mqtt_client._client_id.decode() if mqtt_client._client_id else "Not connected",
        "connected": mqtt_client._userdata["connected"],
        "subscriptions": mqtt_client._userdata.get("subscriptions", []),
        "messages_received": mqtt_client._userdata.get("messages_received", 0)
    }
    return {"broker_info": broker_info, "client_info": client_info}

@app.get("/search_ssids")
async def search_ssids():
    result = subprocess.run(['iwlist', 'wlan0', 'scan'], capture_output=True, text=True)
    ssids = []
    for line in result.stdout.splitlines():
        if "ESSID:" in line:
            ssid = line.split(":")[1].strip().strip('"')
            ssids.append(ssid)
    return {"ssids": ssids}

@app.post("/send_config")
async def send_config(config: DeviceConfig):
    if not config.device_id or not config.ssid or not config.password:
        raise HTTPException(status_code=422, detail="Missing required fields")
    try:
        config_message = {
            "ssid": config.ssid,
            "password": config.password
        }
        mqtt_client.publish(f"stage_tracking/config/{config.device_id}", json.dumps(config_message))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to send configuration: {e}")
        return {"status": "failure", "error": str(e)}

@app.post("/setup_mode")
async def setup_mode():
    try:
        configure_wireless_router()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to configure wireless router: {e}")
        return {"status": "failure", "error": str(e)}

@app.get("/subscriptions")
async def get_subscriptions():
    subscriptions = mqtt_client._userdata["subscriptions"]
    return {"subscriptions": subscriptions}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "get_devices":
                await websocket.send_text(json.dumps(devices))
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
