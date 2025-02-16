import streamlit as st
import requests

FASTAPI_URL = "http://localhost:5000"  # Replace with your FastAPI server URL

def main():
    st.title("SQL Server CRUD Stored Procedure Generator")
    st.write("This app connects to a SQL Server, retrieves database and table information, and generates CRUD stored procedures.")

    # Input for SQL Server name
    server_name = st.text_input("Enter SQL Server name:")

    if server_name:
        # Fetch databases
        response = requests.get(f"{FASTAPI_URL}/databases?server_name={server_name}")
        if response.status_code == 200:
            databases = response.json()["databases"]
            selected_db = st.selectbox("Select a database:", databases)

            # Fetch tables
            response = requests.get(f"{FASTAPI_URL}/tables?server_name={server_name}&database_name={selected_db}")
            if response.status_code == 200:
                tables = response.json()["tables"]
                selected_table = st.selectbox("Select a table:", tables)

                # Fetch table columns
                response = requests.get(f"{FASTAPI_URL}/columns?server_name={server_name}&database_name={selected_db}&table_name={selected_table}")
                if response.status_code == 200:
                    columns = response.json()["columns"]
                    st.subheader("Table Schema")
                    st.table(columns)

                    # Generate stored procedures
                    stored_procedures = generate_crud_stored_procedures(selected_table, columns)
                    st.subheader("Generated Stored Procedures")
                    for sp_name, sp_code in stored_procedures.items():
                        st.write(f"**{sp_name}**")
                        st.code(sp_code, language="sql")

def generate_crud_stored_procedures(table_name, columns):
    def get_column_definition(col):
        if col["type"] in ("varchar", "nvarchar", "char") and col["length"] != -1:
            return f"{col['type']}({col['length']})"
        elif col["type"] == "decimal":
            return f"{col['type']}(18, 2)"
        return col["type"]
    
    primary_key = columns[0]["name"]
    primary_key_type = get_column_definition(columns[0])
    insert_columns = ', '.join([col["name"] for col in columns])
    insert_params = ', '.join([f"@{col['name']} {get_column_definition(col)}" for col in columns])
    insert_values = ', '.join([f"@{col['name']}" for col in columns])
    update_set = ', '.join([f"{col['name']} = @{col['name']}" for col in columns])

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

if __name__ == "__main__":
    main()