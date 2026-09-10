import os
from dotenv import load_dotenv
from google import genai

from services.schema_service import (
    get_database_schema,
    format_schema_for_llm
)

load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_sql(question):
    """
    Convert a natural language question into a MySQL SQL query.
    """

    # Get the latest database schema
    schema = get_database_schema()
    formatted_schema = format_schema_for_llm(schema)

    prompt = f"""
You are an expert MySQL SQL query generator.

Convert the user's natural language question into
a valid MySQL SQL query.

DATABASE SCHEMA:
{formatted_schema}

USER QUESTION:
{question}

RULES:
1. Generate only the SQL query.
2. Do not use markdown code blocks.
3. Use only tables and columns that exist in the schema.
4. Never invent tables or columns.
5. Use foreign-key relationships correctly when JOINs are needed.
6. Use appropriate JOIN, GROUP BY, HAVING, ORDER BY,
   aggregate functions, or subqueries when required.
7. The database is MySQL.
8. Do not explain the query.
9. Select all columns or calculated values necessary to directly answer the user's question.
10. If the question asks for a highest, lowest, average, total, count, percentage, or similar metric, return the calculated value along with the relevant entity.

Return ONLY the SQL query.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    sql = interaction.output_text.strip()

    return sql


def explain_result(question, sql, result):
    """
    Generate a concise natural-language explanation
    of the SQL query result.
    """

    rows = result["rows"]

    # Send only a limited number of rows to Gemini
    # to avoid unnecessarily large prompts.
    preview_rows = rows[:20]

    prompt = f"""
You are an AI database assistant.

USER QUESTION:
{question}

SQL QUERY:
{sql}

QUERY RESULTS:
{preview_rows}

Explain the result to the user in simple and clear language.

RULES:
1. Directly answer the user's question.
2. Mention important numbers, names, or values from the results.
3. If there are no results, clearly say that no matching records were found.
4. Do not explain the SQL query itself unless necessary.
5. Do not invent information that is not present in the query results.
6. Keep the explanation concise, around 2-4 sentences.
7. Return ONLY the explanation.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    explanation = interaction.output_text.strip()

    return explanation


if __name__ == "__main__":

    question = input("Enter your question: ")

    try:
        sql = generate_sql(question)

        print("\nGenerated SQL:")
        print(sql)

    except Exception as e:
        print("\nError:")
        print(e)