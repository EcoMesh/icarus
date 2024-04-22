from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from typing import List, Literal, Annotated, Union
from app.database import get_database
import rethinkdb.query as r
import subprocess
import threading
import json

def generate_drone_path(sensor_coordinates):
    # TODO: implement this function
    pass

app = FastAPI()


class AlertSensor(BaseModel):
    node_id: str
    timestamp: str

class AlertSensorStateChange(BaseModel):
    reason: Literal["sensor_state_change"]
    state: Literal["started", "ended"]
    alarm_id: str
    sensors: List[AlertSensor]


class AlertRegionEvent(BaseModel):
    reason: Literal["event_start", "event_end"]
    alarm_id: str
    alarm_event_id: str

Alert = Annotated[Union[AlertSensorStateChange, AlertRegionEvent], Field(discriminator="reason")]

def run_drone(path_file):
    subprocess.run(["python", "drone/drone_sitl_flight.py", path_file])

@app.post("/webhook")
async def webhook(body: Alert, conn = Depends(get_database)):
    print(body)
    if body.reason == "event_end":
        sensors = await (
            r.table('alarms_event_records')
            .get_all(body.alarm_event_id, index='alarm_event_id')
            .eq_join("node_id", r.table("sensors"), index="node_id")
            .run(conn)
        )

        sensor_coordinates = [
            {
                "longitude": sensor["right"]["location"]["coordinates"][1],
                "latitude": sensor["right"]["location"]["coordinates"][0],
            }
            for sensor in sensors.items
        ]

        drone_path = generate_drone_path(sensor_coordinates)
        
        with open('path.json', 'w') as f:
            f.write(json.dumps(drone_path))
        
        threading.Thread(target=run_drone, args=('path.json',)).start()


        return sensor_coordinates
    return None