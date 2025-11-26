from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
import random
import uvicorn
import csv
import io

app = FastAPI(title = "shibutz haylim", version = "1.0.0")

DB_FILE = "the_base.sqlite"
CSV_FILE = "hayal_300_no_status.csv"

class Solder(BaseModel):
    number : int
    first_name : str
    last_name : str
    gender : str
    city : str
    distance : int
    status : bool
    dorm_charecter : str | None


def init_db():
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
        status INT NOT NULL DEFAULT 0,
        dorm_charecter TEXT DEFAULT NULL
        );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dorms(
        charecter TEXT NOT NULL,
        clear_beds INT NOT NULL,
        space INT NOT NULL DEFAULT 1
        );
    """)    

    conn.commit()
    conn.close()

def solders_row_to_dict(row) -> dict:
    return {
        "number" : row["number"],
        "first_name" : row["first_name"],
        "last_name" : row["last_name"],
        "gender" : row["gender"],
        "city" : row["city"],
        "distance" : row["distance"],
        "status" : row["status"]
    }

def read_solders(status : bool | None = None) ->list[dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if status is not None:
        cursor.execute("SELECT * FROM solders WHERE status = ?", (1 if status else 0,))
    else:
        cursor.execute("SELECT * FROM solders")
    
    rows = cursor.fetchall()
    conn.close()

    return [solders_row_to_dict(row) for row in rows]

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
  
    return solders_row_to_dict(row)

def delete_solder(solder_number : int) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM solders WHERE number = ?",(solder_number,))
    if not cursor.fetchone:
        conn.close()
        return False
    
    cursor.execute("DELETE FROM solders WHERE id = ?", (solder_number,))
    conn.commit()
    conn.close
    return True

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

def read_dorms(space : bool | None = None) ->list[dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if space is not None:
        cursor.execute("SELECT * FROM dorms WHERE space = ?", (1 if space else 0,))
    else:
        cursor.execute("SELECT * FROM dorms")

    rows = cursor.fetchall()
    conn.close()
    rows_list = []
    for row in rows:
        dorm_row = {
            "charecter" : row["charecter"],
            "clear_beds" : row["clear_beds"],
            "space" : row["space"]
        }
        rows_list.append(dorm_row)

    return rows_list
read_dorms()
def create_dorm(dorm_charecter : str) -> dict:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO dorms (charecter, clear_beds, space)
    VALUES (?, ?, ?)
""", (dorm_charecter, 8, 1))
    

    conn.commit()
    conn.close()

    row = {
        "charecter" : dorm_charecter,
        "clear_beds" : 8,
        "space" : True
    }
    return row

def delete_dorm(dorm_charecter : int) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dorms droms WHERE charecter = ?",(dorm_charecter,))
    if not cursor.fetchone:
        conn.close()
        return False
    
    cursor.execute("DELETE FROM dorms WHERE charecter = ?", (dorm_charecter,))
    conn.commit()
    conn.close
    return True

def add_solder_to_dorm() -> dict | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dorms WHERE space = ?", (1,))
    if not cursor.fetchall():
        return None
    
    row = cursor.fetchone()
    row["clear_beds"] -= 1
    
    dorm_row = {
    "charecter" : row["charecter"],
    "clear_beds" : row["clear_beds"],
    "space" : row["space"]
    }
    return dorm_row

@app.get("/")
def read_root():
    return {"massage" : "Welcome to base shivat hashibolim"}

@app.get("/solders", response_model = list[Solder])
def get_all_solders():
    solders = read_solders()
    return solders

@app.get("/solders/{status}")
def get_solders_by_status(solders_status):
    solders = read_solders(status = solders_status)
    return solders

@app.post("/solders/post")
def import_solders_from_csv():
    return import_from_csv(DB_FILE)

@app.post("/solders/add_solder")
def add_solder_to_clear_dorm():
    if add_solder_to_dorm():
        return add_solder_to_dorm()
    else:
        sorry = "sorry, there is no clear dorms, this solder transpering to wait list"
        return sorry
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 