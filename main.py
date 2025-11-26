from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uvicorn
import csv
import io

app = FastAPI(title = "shibutz haylim", version = "1.0.0")

DB_FILE = "hayal_300_no_status.sqlite"

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

def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solders (
        number INT PRIMARY KEY NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        city TEXT NOT NULL,
        distance INT NOT NULL,
        status INT NOT NULL DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()

def row_to_dict(row) -> dict:
    return {
        "number" : row["number"],
        "first_name" : row["first_name"],
        "last_name" : row["last_name"],
        "gender" : row["gender"],
        "city" : row["city"],
        "distance" : row["distance"],
        "status" : row["status"]
    }

