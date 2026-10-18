
from database.connection import engine
from sqlalchemy import text
import sqlglot
from sqlglot import exp


def clean_sql(sql):
    """Remove markdown code fences and surrounding whitespace."""
    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def get_sqlglot_dialect():
    """Match SQL parsing to the active database."""
    dialect = engine.dialect.name.lower()

    if dialect == "postgresql":
        return "postgres"
    if dialect == "mysql":
        return "mysql"

    raise ValueError(f"Unsupported database dialect: {dialect}")


def validate_sql(sql):
    """Allow exactly one read-only SELECT query."""
    sql = clean_sql(sql)

    if not sql:
        raise ValueError("Generated SQL is empty.")

    dialect = get_sqlglot_dialect()

    try:
        parsed = sqlglot.parse(sql, read=dialect)
    except Exception as e:
        raise ValueError(f"Invalid SQL syntax: {e}") from e

    if len(parsed) != 1 or parsed[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    statement = parsed[0]

    # Only SELECT statements, including read-only CTE queries.
    if not isinstance(statement, exp.Query):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject SELECT statements containing data-changing operations.
    for node in statement.walk():
        if isinstance(
            node,
            (
                exp.Insert,
                exp.Update,
                exp.Delete,
                exp.Merge,
                exp.Create,
                exp.Drop,
                exp.Alter,
                exp.Command,
            ),
        ):
            raise ValueError("Only read-only SELECT queries are allowed.")

    return sql


def execute_sql(sql):
    """Validate and execute a read-only query."""
    sql = validate_sql(sql)

    try:
        with engine.connect() as connection:
            # PostgreSQL read-only transaction protection.
            if engine.dialect.name == "postgresql":
                connection.execute(
                    text("SET TRANSACTION READ ONLY")
                )

            result = connection.execute(text(sql))

            columns = list(result.keys())
            rows = [
                dict(row._mapping)
                for row in result
            ]

            return {
                "columns": columns,
                "rows": rows,
            }

    except Exception as e:
        raise RuntimeError(f"SQL execution failed: {e}") from e


if __name__ == "__main__":
    sql = input("Enter SQL query: ")

    try:
        result = execute_sql(sql)
        print("\nColumns:", result["columns"])
        print("\nResults:")

        for row in result["rows"]:
            print(row)

        if not result["rows"]:
            print("No results found.")

    except Exception as e:
        print("\nError:", e)
