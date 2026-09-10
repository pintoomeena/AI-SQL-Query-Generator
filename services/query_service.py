from services.llm_service import generate_sql
from services.sql_service import execute_sql
from services.schema_service import (
    get_database_schema,
    format_schema_for_llm
)

from google import genai
import os
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def repair_sql(question, sql, error):
    """
    Ask Gemini to repair SQL using the database error.
    """

    schema = get_database_schema()
    formatted_schema = format_schema_for_llm(schema)

    prompt = f"""
You are an expert MySQL SQL debugger.

USER QUESTION:
{question}

DATABASE SCHEMA:
{formatted_schema}

GENERATED SQL:
{sql}

MYSQL ERROR:
{error}

Fix the SQL query.

RULES:
1. Return ONLY the corrected SQL query.
2. Do not use markdown code blocks.
3. Use only tables and columns from the schema.
4. The corrected query must be read-only.
5. The database is MySQL.
6. Do not explain anything.

CORRECTED SQL:
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text.strip()


def process_question(question, max_retries=2):
    """
    Generate SQL, execute it, and automatically
    repair it if MySQL returns an error.
    """

    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)

    for attempt in range(max_retries + 1):

        try:

            result = execute_sql(sql)

            return {
                "sql": sql,
                "result": result,
                "attempts": attempt + 1
            }

        except Exception as error:

            print("\nSQL Error:")
            print(error)

            if attempt == max_retries:

                raise RuntimeError(
                    f"SQL failed after {max_retries + 1} attempts."
                )

            print("\nAttempting SQL repair...")

            sql = repair_sql(
                question,
                sql,
                str(error)
            )

            print("\nCorrected SQL:")
            print(sql)

if __name__ == "__main__":
    question = input("Ask your database a question: ")

    try:
        response = process_question(question)

        print("\nFinal Results:")

        if not response["result"]["rows"]:
            print("No results found.")
        else:
            for row in response["result"]["rows"]:
                print(row)

        print(f"\nAttempts: {response['attempts']}")

    except Exception as e:
        print("\nError:")
        print(e)