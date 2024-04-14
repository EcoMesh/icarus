from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from app.database import get_database



app = FastAPI()


class AlertSensor(BaseModel):
    node_id: str
    timestamp: str

class Alert(BaseModel):
    reason: str
    state: str
    alarm_id: str
    region_id: str
    sensors: List[AlertSensor]

@app.post("/webhook")
def webhook(body: Alert, conn = Depends(get_database)):
    print(body)
    
    return "Hello World!"