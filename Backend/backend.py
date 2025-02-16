from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

def connect_to_sql_server(server_name):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};"
            f"Server={server_name};"
            f"Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        return str(e)

@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route("/databases", methods=["GET"])
def get_databases():
    server_name = request.args.get("server_name")
    conn = connect_to_sql_server(server_name)
    if isinstance(conn, str):
        return jsonify({"error": conn}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
    databases = [row.name for row in cursor.fetchall()]
    conn.close()
    return jsonify({"databases": databases})

@app.route("/tables", methods=["GET"])
def get_tables():
    server_name = request.args.get("server_name")
    database_name = request.args.get("database_name")
    conn = connect_to_sql_server(server_name)
    if isinstance(conn, str):
        return jsonify({"error": conn}), 500
    cursor = conn.cursor()
    cursor.execute(f"USE [{database_name}];")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tables = [row.TABLE_NAME for row in cursor.fetchall()]
    conn.close()
    return jsonify({"tables": tables})

@app.route("/columns", methods=["GET"])
def get_columns():
    server_name = request.args.get("server_name")
    database_name = request.args.get("database_name")
    table_name = request.args.get("table_name")
    conn = connect_to_sql_server(server_name)
    if isinstance(conn, str):
        return jsonify({"error": conn}), 500
    cursor = conn.cursor()
    cursor.execute(f"USE [{database_name}];")
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
    """)
    columns = [{"name": row.COLUMN_NAME, "type": row.DATA_TYPE, "length": row.CHARACTER_MAXIMUM_LENGTH} for row in cursor.fetchall()]
    conn.close()
    return jsonify({"columns": columns})

if __name__ == "__main__":
    app.run()
