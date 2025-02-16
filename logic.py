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