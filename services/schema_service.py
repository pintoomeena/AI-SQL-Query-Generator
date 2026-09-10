from database.connection import engine
from sqlalchemy import inspect


def get_database_schema():
    inspector = inspect(engine)

    schema = {}

    # Get all tables
    tables = inspector.get_table_names()

    for table in tables:

        # Get columns
        columns = inspector.get_columns(table)

        # Get primary key information
        primary_key = inspector.get_pk_constraint(table)
        primary_key_columns = primary_key.get("constrained_columns", [])

        # Get foreign key information
        foreign_keys = inspector.get_foreign_keys(table)

        # Store table information
        schema[table] = {
            "columns": [],
            "primary_keys": primary_key_columns,
            "foreign_keys": []
        }

        # Process columns
        for column in columns:
            schema[table]["columns"].append({
                "name": column["name"],
                "type": str(column["type"])
            })

        # Process foreign keys
        for fk in foreign_keys:
            for i, column in enumerate(fk["constrained_columns"]):

                schema[table]["foreign_keys"].append({
                    "column": column,
                    "references_table": fk["referred_table"],
                    "references_column": fk["referred_columns"][i]
                })

    return schema


def format_schema_for_llm(schema):

    formatted_schema = ""

    for table, table_info in schema.items():

        formatted_schema += f"Table: {table}\n"

        # Columns
        formatted_schema += "Columns:\n"

        for column in table_info["columns"]:

            column_name = column["name"]
            column_type = column["type"]

            if column_name in table_info["primary_keys"]:
                formatted_schema += (
                    f"  - {column_name} ({column_type}) [PRIMARY KEY]\n"
                )
            else:
                formatted_schema += (
                    f"  - {column_name} ({column_type})\n"
                )

        # Foreign keys
        if table_info["foreign_keys"]:

            formatted_schema += "Relationships:\n"

            for fk in table_info["foreign_keys"]:

                formatted_schema += (
                    f"  - {fk['column']} "
                    f"→ {fk['references_table']}.{fk['references_column']}\n"
                )

        formatted_schema += "\n"

    return formatted_schema


if __name__ == "__main__":

    schema = get_database_schema()

    formatted_schema = format_schema_for_llm(schema)

    print(formatted_schema)