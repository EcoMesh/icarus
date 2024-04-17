from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from typing import List, Literal, Annotated, Union
from app.database import get_database
import rethinkdb.query as r


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
    if body.reason == "event_end":
        sensors = await (
            r.table('alarms_event_records')
            .get_all(body.alarm_event_id, index='alarm_event_id')
            .eq_join("node_id", r.table("sensors"), index="node_id")
            .run(conn)
        )

        coordinates = [
            {
                "latitude": sensor["right"]["location"]["coordinates"][0],
                "longitude": sensor["right"]["location"]["coordinates"][1],
            }
            for sensor in sensors.items
        ]
        
        return coordinates
    return None