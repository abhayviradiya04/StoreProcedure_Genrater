import pyodbc
from tabulate import tabulate
import streamlit as st

def connect_to_sql_server(server_name):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};"
            f"Server={server_name};"
            f"Trusted_Connection=yes;"
        )
        st.success("Connected to SQL Server successfully!")
        return conn
    except Exception as e:
        st.error(f"Error connecting to SQL Server: {e}")
        return None

def fetch_databases(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
    return [row.name for row in cursor.fetchall()]

def fetch_tables(conn, database_name):
    cursor = conn.cursor()
    cursor.execute(f"USE [{database_name}];")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return [row.TABLE_NAME for row in cursor.fetchall()]

def fetch_table_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
    """)
    return cursor.fetchall()

def generate_crud_stored_procedures(table_name, columns):
    def get_column_definition(col):
        if col[1] in ("varchar", "nvarchar", "char") and col[2] != -1:
            return f"{col[1]}({col[2]})"
        elif col[1] == "decimal":
            return f"{col[1]}(18, 2)"
        return col[1]
    
    primary_key = columns[0][0]
    primary_key_type = get_column_definition(columns[0])
    insert_columns = ', '.join([col[0] for col in columns])
    insert_params = ', '.join([f"@{col[0]} {get_column_definition(col)}" for col in columns])
    insert_values = ', '.join([f"@{col[0]}" for col in columns])
    update_set = ', '.join([f"{col[0]} = @{col[0]}" for col in columns])

    return {
        "SelectAll": f"""
CREATE PROCEDURE SP_{table_name}_SelectAll
AS
BEGIN
    SELECT * FROM {table_name};
END
GO
""",
        "SelectByPK": f"""
CREATE PROCEDURE SP_{table_name}_SelectByPK
@Id {primary_key_type}
AS
BEGIN
    SELECT * FROM {table_name} 
    WHERE {primary_key} = @Id;
END
GO
""",
        "Insert": f"""
CREATE PROCEDURE SP_{table_name}_Insert
{insert_params}
AS
BEGIN
    INSERT INTO {table_name} ({insert_columns}) VALUES 
    ({insert_values});
END
GO
""",
        "Update": f"""
CREATE PROCEDURE SP_{table_name}_Update
@Id {primary_key_type},
{insert_params}
AS
BEGIN
    UPDATE {table_name} SET {update_set} 
    WHERE {primary_key} = @Id;
END
GO
""",
        "Delete": f"""
CREATE PROCEDURE SP_{table_name}_Delete 
@Id {primary_key_type}
AS
BEGIN
    DELETE FROM {table_name} 
    WHERE {primary_key} = @Id;
END
GO
"""
    }

def main():
    st.title("SQL Server CRUD Stored Procedure Generator")
    st.write("This app connects to a SQL Server, retrieves database and table information, and generates CRUD stored procedures.")

    # Input for SQL Server name
    server_name = st.text_input("Enter SQL Server name:")

    if server_name:
        conn = connect_to_sql_server(server_name)
        if conn:
            # Fetch databases
            databases = fetch_databases(conn)
            if databases:
                selected_db = st.selectbox("Select a database:", databases)

                # Fetch tables
                tables = fetch_tables(conn, selected_db)
                if tables:
                    selected_table = st.selectbox("Select a table:", tables)

                    # Fetch table columns
                    columns = fetch_table_columns(conn, selected_table)
                    if columns:
                        st.subheader("Table Schema")
                        st.table(columns)

                        # Generate stored procedures
                        stored_procedures = generate_crud_stored_procedures(selected_table, columns)
                        st.subheader("Generated Stored Procedures")
                        for sp_name, sp_code in stored_procedures.items():
                            st.write(f"**{sp_name}**")
                            st.code(sp_code, language="sql")

            conn.close()

if __name__ == "__main__":
    main()