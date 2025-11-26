from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uvicorn
import csv
import io

app = FastAPI(title = "shibutz haylim", version = "1.0.0")

app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response

