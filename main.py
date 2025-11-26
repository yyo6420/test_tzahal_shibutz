from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
import random
import uvicorn
import csv
import io

app = FastAPI(title = "shibutz haylim", version = "1.0.0")

DB_FILE = "hayal_300_no_status.sqlite"
CSV_FILE = "hayal_300_no_status.csv"

class Solder(BaseModel):
    number : int
    first_name : str
    last_name : str
    gender : str
    city : str
    distance : int
    status : bool

class Dorm(BaseModel):
    charecter : str
    clear_beds : int
    space : bool


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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dorms(
    charecter TEXT NOT NULL,
    clear_beds INT NOT NULL
    space INT NOT NULL DEFAULT 1
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

def raed_solders(status : bool | None = None) ->list[dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if status is not None:
        cursor.execute("SELECT * FROM solders WHERE status = ?", (1 if status else 0,))
    else:
        cursor.execute("SELECT * FROM solders")
    
    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]

def create_solder(solder : Solder) -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO solders (number, first_name, last_name, gender, city, distance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", solder.number, solder.first_name, solder.last_name, solder.gender, solder.city, solder.distance, 1 if solder.status else 0)
    
    row = cursor.fetchone()

    conn.commit()
    conn.close()

    return row_to_dict(row)

def import_from_csv(csv_content : bytes) -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        csv_text = csv_content.decode("utf-8")
        csv_raeder = csv.DictReader(io.StringIO(csv_text))
    
        import_count = 0

        for row in csv_raeder:
            number = row.get("number")
            if number[0] != 8:
                continue

            first_name = row.get("first_name")
            last_name = row.get("last_name")
            gender = row.get("gender")
            city = row.get("city")
            distance = row.get("distance")
            status = 1 if row.get("status") else 0

            cursor.execute("""
                INSERT INTO solders (number, first_name, last_name, gender, city, distance, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (number, first_name, last_name, gender, city, distance, status))
            import_count += 1
        
        conn.commit()

        return {
            "message": f"Successfully imported {import_count} solders from CSV",
        }

    except Exception as error:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(error)}")
    finally:
        conn.close()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)