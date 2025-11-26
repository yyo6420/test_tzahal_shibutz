from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uvicorn
import csv
import io

app = FastAPI(title = "shibutz haylim", version = "1.0.0")

BD_FILE = "hayal_300_no_status.sqlite"

class Solder(BaseModel):
    number : int
    first_name : str
    last_name : str
    gender : str
    city : str
    distance : int
    status : bool

class Room(BaseModel):
    clear_beds : int

class Dorm(BaseModel):
    room_with_clear_beds : int

