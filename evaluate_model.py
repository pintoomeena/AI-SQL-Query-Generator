import os
import json
from dotenv import load_dotenv
from google import genai

from services.schema_service import (
    get_database_schema,
    format_schema_for_llm
)
from services.sql_service import execute_sql


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


QUESTIONS = [
    # Basic SELECT / Filtering
    "Show me all employees.",
    "Show the names and salaries of all employees.",
    "Show employees earning more than 100000.",
    "Show employees earning less than 80000.",
    "Show all currently active projects.",

    # JOIN queries
    "Which employees work in the Engineering department?",
    "Show the names of employees along with their department names.",
    "Show all employees working in the Data Science department.",
    "Show employees and the projects they are assigned to.",
    "Show each project along with the names of employees working on it.",

    # Aggregation
    "What is the average salary of each department?",
    "How many employees are in each department?",
    "What is the highest salary in the company?",
    "What is the lowest salary in the company?",
    "What is the average performance rating for each department?",

    # GROUP BY / HAVING
    "Which employees are working on more than one project?",
    "Which department has the highest number of employees?",
    "Which projects have more than two employees assigned to them?",
    "Which departments have an average salary greater than 100000?",
    "Which employees have a performance rating above 4?",

    # Ranking / Ordering
    "Which department has the highest average salary?",
    "Who are the top 5 highest-paid employees?",
    "Which project has the highest budget?",
    "Show the three employees with the highest salaries.",
    "Which department has the lowest average salary?",

    # Performance / Employee analysis
    "Show employees with a performance rating below 3.",
    "Show the employee with the highest performance rating.",
    "Show the average performance rating of all employees.",
    "Which employees have received more than one performance review?",
    "Show employees who are working on at least one project."
]


def generate_sql(question):
    schema = get_database_schema()
    formatted_schema = format_schema_for_llm(schema)

    prompt = f"""
You are an expert MySQL SQL generator.

USER QUESTION:
{question}

DATABASE SCHEMA:
{formatted_schema}

RULES:
1. Return ONLY the SQL query.
2. Do not use markdown.
3. Use only tables and columns from the schema.
4. Use the correct foreign-key relationships.
5. The database is MySQL.
6. Generate a read-only SELECT query.
7. The query must directly answer the user's question.

SQL:
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text.strip()


def run_evaluation():

    correct = 0
    total = len(QUESTIONS)

    results = []

    for i, question in enumerate(QUESTIONS, start=1):

        print("\n" + "=" * 70)
        print(f"Question {i}/{total}")
        print(question)

        generated_sql = None

        try:
            generated_sql = generate_sql(question)

            print("\nGenerated SQL:")
            print(generated_sql)

            result = execute_sql(generated_sql)

            print("\nExecution: SUCCESS")

            correct += 1

            results.append({
                "question": question,
                "sql": generated_sql,
                "execution_success": True
            })

        except Exception as e:

            print("\nExecution: FAILED")
            print(e)

            results.append({
                "question": question,
                "sql": generated_sql,
                "execution_success": False,
                "error": str(e)
            })

    accuracy = (correct / total) * 100

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(f"Total questions: {total}")
    print(f"Successful queries: {correct}")
    print(f"Execution success rate: {accuracy:.2f}%")

    with open("evaluation_results.json", "w") as file:
        json.dump(results, file, indent=4, default=str)

    print("\nResults saved to evaluation_results.json")


if __name__ == "__main__":
    run_evaluation()
