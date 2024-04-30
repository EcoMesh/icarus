from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from typing import List, Literal, Annotated, Union
from app.database import get_database
import rethinkdb.query as r
import threading

from app.pathfinder import generate_drone_path_with_homebase, LAUNCH_SITE
from app.drone_controller import run_drone



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


@app.post("/webhook")
async def webhook(body: Alert, conn = Depends(get_database)):
    print(body)
    if body.reason == "event_end":
        sensors = await (
            r.table('alarms_event_records')
            .get_all(body.alarm_event_id, index='alarm_event_id')
            .pluck('node_id')
            .distinct()
            .eq_join("node_id", r.table("sensors"), index="node_id")
            .run(conn)
        )

        sensor_coordinates = [
            tuple(reversed(sensor["right"]["location"]["coordinates"]))
            for sensor in sensors
        ]

        drone_path = generate_drone_path_with_homebase(sensor_coordinates)
        
        threading.Thread(target=run_drone, args=(drone_path, LAUNCH_SITE)).start()

        return drone_path
    return None