from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/db-test")
def db_test():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "database": "connected",
            "result": result[0]
        }
    
    except Exception as e:
        return {
            "status": "error",
            "database": "not connected",
            "error": str(e)
        }

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}