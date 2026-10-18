
import os

from dotenv import load_dotenv
from google import genai

from database.connection import engine
from services.llm_service import generate_sql
from services.sql_service import execute_sql
from services.schema_service import (
    get_database_schema,
    format_schema_for_llm,
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


def repair_sql(question, sql, error):
    """Ask Gemini to repair SQL using the active database dialect."""
    if client is None:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    dialect = engine.dialect.name.lower()
    schema = get_database_schema()
    formatted_schema = format_schema_for_llm(schema)

    prompt = f"""
You are an expert {dialect} SQL debugger.

USER QUESTION:
{question}

DATABASE DIALECT:
{dialect}

DATABASE SCHEMA:
{formatted_schema}

GENERATED SQL:
{sql}

DATABASE ERROR:
{error}

Correct the SQL for the specified database dialect.

RULES:
1. Return ONLY the corrected SQL query.
2. Do not use markdown code blocks.
3. Use only tables and columns from the schema.
4. Return exactly one read-only SELECT query.
5. Do not use INSERT, UPDATE, DELETE, MERGE, CREATE, DROP, or ALTER.
6. Use {dialect}-compatible SQL syntax.
7. Do not explain anything.

CORRECTED SQL:
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    return interaction.output_text.strip()


def process_question(question, max_retries=2):
    """Generate, execute and repair SQL if necessary."""
    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)

    for attempt in range(max_retries + 1):
        try:
            result = execute_sql(sql)

            return {
                "sql": sql,
                "result": result,
                "attempts": attempt + 1,
            }

        except Exception as error:
            print("\nSQL Error:")
            print(error)

            if attempt == max_retries:
                raise RuntimeError(
                    f"SQL failed after {max_retries + 1} attempts."
                ) from error

            print("\nAttempting SQL repair...")

            sql = repair_sql(
                question,
                sql,
                str(error),
            )

            print("\nCorrected SQL:")
            print(sql)

    raise RuntimeError("SQL processing failed unexpectedly.")


if __name__ == "__main__":
    question = input("Ask your database a question: ")

    try:
        response = process_question(question)
        print("\nFinal Results:")

        for row in response["result"]["rows"]:
            print(row)

        if not response["result"]["rows"]:
            print("No results found.")

        print(f"\nAttempts: {response['attempts']}")

    except Exception as e:
        print("\nError:")
        print(e)
