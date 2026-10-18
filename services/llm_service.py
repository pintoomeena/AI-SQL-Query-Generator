
import os
from dotenv import load_dotenv
from google import genai

from database.connection import engine
from services.schema_service import (
    get_database_schema,
    format_schema_for_llm,
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


def get_database_dialect():
    """Return the dialect of the active database."""
    dialect = engine.dialect.name.lower()

    if dialect not in ("mysql", "postgresql"):
        raise RuntimeError(f"Unsupported database dialect: {dialect}")

    return dialect


def generate_sql(question):
    """Convert a natural-language question into database-specific SQL."""
    if client is None:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    dialect = get_database_dialect()
    schema = get_database_schema()
    formatted_schema = format_schema_for_llm(schema)

    prompt = f"""
You are an expert {dialect} SQL query generator.

Convert the user's natural-language question into a valid
SQL query for the {dialect} database.

DATABASE DIALECT:
{dialect}

DATABASE SCHEMA:
{formatted_schema}

USER QUESTION:
{question}

RULES:
1. Return only one SQL query.
2. Do not use markdown code blocks.
3. Use only tables and columns present in the schema.
4. Never invent tables or columns.
5. Use foreign-key relationships correctly when JOINs are needed.
6. Use appropriate JOIN, GROUP BY, HAVING, ORDER BY,
   aggregate functions, or subqueries when required.
7. Use syntax compatible with {dialect}.
8. Do not explain the query.
9. Select the columns or calculated values needed to answer the question.
10. For highest, lowest, average, total, count, or percentage questions,
    return the calculated value and relevant entity where appropriate.
11. Generate a read-only SELECT query only.
12. Do not generate INSERT, UPDATE, DELETE, MERGE, CREATE, DROP, or ALTER.

Return ONLY the SQL query.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    sql = interaction.output_text.strip()

    if not sql:
        raise RuntimeError("Gemini returned an empty SQL query.")

    return sql


def explain_result(question, sql, result):
    """Generate a concise explanation based on the query results."""
    if client is None:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    preview_rows = result["rows"][:20]

    prompt = f"""
You are an AI database assistant.

USER QUESTION:
{question}

SQL QUERY:
{sql}

QUERY RESULTS:
{preview_rows}

Explain the result in simple and clear language.

RULES:
1. Directly answer the user's question.
2. Mention important numbers, names, or values from the results.
3. If there are no results, clearly say so.
4. Do not explain the SQL unless necessary.
5. Do not invent information not present in the results.
6. Keep the explanation concise, around 2-4 sentences.
7. Return only the explanation.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    return interaction.output_text.strip()


if __name__ == "__main__":
    question = input("Enter your question: ")

    try:
        sql = generate_sql(question)
        print("\nGenerated SQL:")
        print(sql)
    except Exception as e:
        print("\nError:")
        print(e)
