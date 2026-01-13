from fastapi import FastAPI
import pyodbc

app = FastAPI()

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=YOUR_SERVER;"
        "DATABASE=YOUR_DB;"
        "UID=YOUR_USER;"
        "PWD=YOUR_PASSWORD;"
        "Encrypt=No;"
        "TrustServerCertificate=Yes;"
    )

@app.get("/views")
def get_views():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.views ORDER BY name")
    data = [row[0] for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/procedures")
def get_procedures():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.procedures ORDER BY name")
    data = [row[0] for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/definition")
def get_definition(object_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT OBJECT_DEFINITION(OBJECT_ID(?))",
        object_name
    )
    row = cursor.fetchone()
    conn.close()
    return {"definition": row[0] if row else ""}
