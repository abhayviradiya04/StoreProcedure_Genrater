import os
import uvicorn
from fastapi import FastAPI, HTTPException
import pyodbc

app = FastAPI()

def connect_to_sql_server(server_name):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};"
            f"Server={server_name};"
            f"Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Backend is running!"}

@app.get("/databases")
def get_databases(server_name: str):
    conn = connect_to_sql_server(server_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
    databases = [row.name for row in cursor.fetchall()]
    conn.close()
    return {"databases": databases}

@app.get("/tables")
def get_tables(server_name: str, database_name: str):
    conn = connect_to_sql_server(server_name)
    cursor = conn.cursor()
    cursor.execute(f"USE [{database_name}];")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tables = [row.TABLE_NAME for row in cursor.fetchall()]
    conn.close()
    return {"tables": tables}

@app.get("/columns")
def get_columns(server_name: str, database_name: str, table_name: str):
    conn = connect_to_sql_server(server_name)
    cursor = conn.cursor()
    cursor.execute(f"USE [{database_name}];")
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
    """)
    columns = [{"name": row.COLUMN_NAME, "type": row.DATA_TYPE, "length": row.CHARACTER_MAXIMUM_LENGTH} for row in cursor.fetchall()]
    conn.close()
    return {"columns": columns}

if __name__ == "__main__":
    app.run(debug=False)