from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import json
import os
import subprocess
import asyncio
import sqlite3
from utils.mqtt_utils import mqtt_client, start_mqtt_client, get_ip_address
from utils.logging_utils import logger, initialize_db, fetch_logs, active_websockets, process_log_queue, get_anchor_points
from utils.network_utils import get_ip_address 

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class DeviceConfig(BaseModel):
    device_id: str
    ssid: str
    password: str

class ModeChangeRequest(BaseModel):
    mode: str

class UpdateAnchorPosition(BaseModel):
    id: str
    webpage_x: int
    webpage_y: int

class AnchorUpdate(BaseModel):
    mac_address: str
    user_defined_name: str
    user_defined_location: str

current_mode = "Unknown"
devices = []

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_log_queue())

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
    result = subprocess.run(['sudo', 'iwlist', 'wlan0', 'scan'], capture_output=True, text=True)
    ssids = [line.split(":")[1].strip().strip('"') for line in result.stdout.splitlines() if "ESSID:" in line]
    return {"ssids": list(set(ssids))}

@app.post("/send_config")
async def send_config(config: DeviceConfig):
    if not config.device_id or not config.ssid or not config.password:
        raise HTTPException(status_code=422, detail="Missing required fields")
    try:
        config_message = {
            "type": "system_setup",
            "ssid": config.ssid,
            "password": config.password
        }
        device_ids = ["device_1", "device_2", "device_3"] if config.device_id == 'all' else [config.device_id]
        for device_id in device_ids:
            mqtt_client.publish(f"stage_tracking/config/{device_id}", json.dumps(config_message))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to send configuration: {e}")
        return {"status": "failure", "error": str(e)}

@app.post("/change_mode")
async def change_mode(mode_request: ModeChangeRequest):
    global current_mode
    if mode_request.mode not in ["setup", "calibration", "show"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    current_mode = mode_request.mode
    logger.info(f"Mode changed to {current_mode}")
    for websocket in active_websockets:
        await websocket.send_text(f"Mode changed to {current_mode}")
    return {"status": "success", "mode": current_mode}

@app.get("/get_mode")
async def get_mode():
    return {"mode": current_mode}

@app.get("/subscriptions")
async def get_subscriptions():
    subscriptions = mqtt_client._userdata["subscriptions"]
    return {"subscriptions": subscriptions}

@app.get("/logs")
async def get_logs():
    logs = fetch_logs()
    return {"logs": [{"timestamp": log[0], "level": log[1], "message": log[2]} for log in logs]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

@app.get("/anchor_points")
async def anchor_points_endpoint():
    anchor_points = get_anchor_points()
    formatted_anchor_points = [
        {
            "id": anchor[0],
            "webpage_x": anchor[1],
            "webpage_y": anchor[2],
            "x_coordinate": anchor[3],
            "y_coordinate": anchor[4],
            "z_coordinate": anchor[5],
            "status": anchor[6],
            "last_updated": anchor[7],
            "firmware_version": anchor[8],
            "user_defined_name": anchor[9],
            "user_defined_location": anchor[10],
            "mac_address": anchor[11],
            "ip_address": anchor[12]
        }
        for anchor in anchor_points
    ]
    return {"anchor_points": formatted_anchor_points}





@app.post("/update_anchor_position")
async def update_anchor_position(position_update: UpdateAnchorPosition):
    try:
        conn = sqlite3.connect('logs.db')
        c = conn.cursor()
        c.execute('''
            UPDATE anchor_points 
            SET webpage_x = ?, webpage_y = ? 
            WHERE id = ?
        ''', (position_update.webpage_x, position_update.webpage_y, position_update.id))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update anchor position: {e}")
        return {"status": "failure", "error": str(e)}


@app.post("/update_anchor")
async def update_anchor(anchor_update: AnchorUpdate):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE anchor_points
        SET user_defined_name = ?, user_defined_location = ?
        WHERE mac_address = ?
    """, (anchor_update.user_defined_name, anchor_update.user_defined_location, anchor_update.mac_address))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/device_ids")
async def get_device_ids():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mac_address, ip_address, user_defined_name, user_defined_location FROM anchor_points")
    device_ids = cursor.fetchall()
    conn.close()
    formatted_device_ids = [
        f"{row[0]} - {row[1]} - {row[2] or ''} - {row[3] or ''}" for row in device_ids
    ]
    return {"device_ids": formatted_device_ids}

@app.get("/anchor_macs")
async def get_anchor_macs():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mac_address, ip_address, user_defined_name, user_defined_location FROM anchor_points")
    anchor_macs = cursor.fetchall()
    conn.close()
    formatted_anchor_macs = [
        f"{row[0]} - {row[1]} - {row[2] or ''} - {row[3] or ''}" for row in anchor_macs
    ]
    return {"anchor_macs": formatted_anchor_macs}

@app.get("/get_anchor_details/{mac_address}")
async def get_anchor_details(mac_address: str):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_defined_name, user_defined_location FROM anchor_points WHERE mac_address = ?", (mac_address,))
    anchor = cursor.fetchone()
    conn.close()
    if anchor:
        return {"user_defined_name": anchor[0], "user_defined_location": anchor[1]}
    else:
        raise HTTPException(status_code=404, detail="Anchor not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
