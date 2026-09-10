# 🗄️ AI SQL Query Generator

An AI-powered SQL Query Generator that allows users to interact with a relational MySQL database using natural language.

Instead of manually writing SQL queries, users can ask questions such as:

- "Show me all employees"
- "What is the average salary of each department?"
- "Which department has the highest average salary?"
- "Which employees are working on more than one project?"

The application uses Gemini to convert natural language questions into SQL queries, validates the generated SQL, executes it on MySQL, and automatically attempts to repair SQL queries if execution errors occur.

---

## 🚀 Features

### 1. Natural Language to SQL

Users can ask database questions in plain English.

Example:

```text
Which department has the highest average salary?

The system generates an SQL query such as:

SELECT d.name, AVG(e.salary) AS average_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY average_salary DESC
LIMIT 1;


2. Automatic Database Schema Extraction

The application automatically reads the MySQL database schema using SQLAlchemy.

It extracts:

Tables
Columns
Data types
Primary keys
Foreign keys
Table relationships

This schema information is provided to Gemini so that SQL queries are generated according to the actual database structure.

3. SQL Validation

Generated SQL is validated using SQLGlot before execution.

The system checks that:

SQL syntax is valid
Only one SQL statement is provided
Only SELECT queries are allowed

Non-read queries such as:

DELETE FROM employees;

are rejected.


4. SQL Execution

Validated SQL queries are executed against the MySQL database using SQLAlchemy.

The results are displayed in a structured table inside the Streamlit application.

5. Automatic SQL Error Repair

If the generated SQL fails during execution, the application sends:

User question
Database schema
Generated SQL
MySQL error

back to Gemini.

Gemini then generates a corrected SQL query and the system retries execution.

Example:

Generated SQL:
SELECT full_name FROM employees;

Error:
Unknown column 'full_name' in 'field list'

The repair system can generate:

SELECT name FROM employees;
6. AI Result Explanation

After successful query execution, Gemini generates a short natural-language explanation of the result.

This allows users to understand the output without manually interpreting the SQL result table.

7. Data Visualization

When the query returns suitable numeric and categorical data, the application automatically provides a visualization.

For example:

What is the average salary of each department?

The application can display the department-wise salary values along with a bar chart.

8. Read-Only Query Protection

The current application is designed to allow only SELECT queries.

This prevents generated queries such as:

INSERT
UPDATE
DELETE
DROP
ALTER

from being executed through the application.

Note: For production deployment, stronger database-level read-only permissions and additional SQL restrictions should be implemented.

🏗️ Architecture
                    ┌─────────────────────┐
                    │       User          │
                    │ Natural Language    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Query Service     │
                    │  Workflow Manager   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
     ┌─────────────────────┐       ┌─────────────────────┐
     │   Schema Service    │       │    LLM Service      │
     │                     │       │                     │
     │ Tables              │──────▶│ Gemini              │
     │ Columns             │       │ Natural Language →  │
     │ PKs / FKs           │       │ SQL                 │
     └─────────────────────┘       └──────────┬──────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │    SQL Service      │
                                   │                     │
                                   │ SQL Cleaning        │
                                   │ SQL Validation      │
                                   │ SQL Execution       │
                                   └──────────┬──────────┘
                                              │
                                      ┌───────┴───────┐
                                      │               │
                                   Success          Error
                                      │               │
                                      ▼               ▼
                              ┌──────────────┐  ┌──────────────┐
                              │ MySQL Result │  │ SQL Repair   │
                              │              │  │ via Gemini   │
                              └──────┬───────┘  └──────┬───────┘
                                     │                 │
                                     │                 │
                                     └────────┬────────┘
                                              ▼
                                   ┌─────────────────────┐
                                   │ Results + AI        │
                                   │ Explanation + Chart │
                                   └─────────────────────┘
🗃️ Database Schema

The project uses a relational MySQL database containing six related tables.

Tables
departments

Stores department information.

id
name
location
employees

Stores employee information.

id
name
email
job_title
salary
department_id
joining_date
manager_id
projects

Stores project information.

id
name
budget
status
start_date
end_date
employee_projects

Many-to-many relationship between employees and projects.

employee_id
project_id
role
assigned_date
performance_reviews

Stores employee performance reviews.

id
employee_id
review_date
rating
comments
salaries

Stores historical employee salary records.

id
employee_id
salary
effective_from
🔗 Database Relationships
departments
     │
     │ 1
     │
     ▼
employees
     │
     ├───────────────┐
     │               │
     │               ▼
     │        performance_reviews
     │
     ▼
employee_projects
     │
     ▼
projects

employees
     │
     ▼
salaries

Important relationships include:

employees.department_id
        ↓
departments.id
employee_projects.employee_id
        ↓
employees.id
employee_projects.project_id
        ↓
projects.id
performance_reviews.employee_id
        ↓
employees.id
salaries.employee_id
        ↓
employees.id
🤖 AI Workflow

The main workflow is:

User Question
      ↓
Extract Database Schema
      ↓
Send Question + Schema to Gemini
      ↓
Generate SQL
      ↓
Clean SQL
      ↓
Validate SQL
      ↓
Execute SQL
      ↓
 ┌───────────────┐
 │               │
Success         Error
 │               │
 ▼               ▼
Results       Gemini SQL Repair
 │               │
 ▼               ▼
AI Explanation  Retry
 │
 ▼
Visualization
🔄 SQL Repair Loop

The system supports automatic SQL repair for execution errors.

For example, if Gemini generates:

SELECT full_name FROM employees;

and MySQL returns:

Unknown column 'full_name' in 'field list'

the system sends the error back to Gemini along with the schema.

Gemini can then generate:

SELECT name FROM employees;

The corrected query is validated and executed again.

The system currently supports a limited number of repair attempts to avoid unnecessary API usage.

📊 Example Queries

The application supports analytical queries such as:

Basic Queries
Show me all employees
Show all projects
List all departments
Filtering
Show employees with salary greater than 100000
Show employees who joined after 2023
Aggregation
What is the average salary of each department?
What is the total salary paid by each department?
How many employees are in each department?
Ranking
Which department has the highest average salary?
Who is the highest paid employee?
Which project has the highest budget?
JOIN Queries
Show employees along with their department names
Show employees working on each project
Show employee names and their performance ratings
Complex Analytical Queries
Which employees have a performance rating above 4 and are working on more than one project?
Which department has the highest average employee salary?
Which projects have more than two employees assigned?
🛠️ Tech Stack
Frontend
Streamlit
Backend
Python
Database
MySQL 8
Database Connectivity
SQLAlchemy
PyMySQL
AI
Google Gemini API
google-genai
SQL Processing
SQLGlot
Configuration
Python-dotenv
📁 Project Structure
AI_SQL_QUERY_GENERATOR/
│
├── app.py
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── database/
│   ├── connection.py
│   └── __init__.py
│
├── services/
│   ├── schema_service.py
│   ├── llm_service.py
│   ├── sql_service.py
│   ├── query_service.py
│   └── __init__.py
│
└── venv/
⚙️ Installation
1. Clone the repository
git clone <your-github-repository-url>

Move into the project directory:

cd AI_SQL_QUERY_GENERATOR
2. Create a Virtual Environment
python -m venv venv

Activate it on Windows:

.\venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root.

Example:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=temp

GEMINI_API_KEY=your_gemini_api_key

Do not commit the .env file to GitHub.

The repository includes .env.example as a template.

🗄️ Database Setup

Create the MySQL database:

CREATE DATABASE temp;

Then create the required tables:

departments
employees
projects
employee_projects
performance_reviews
salaries

Populate the tables with sample employee, department, project, salary, and performance data.

The application dynamically extracts the schema, so the SQL generation system does not depend on a hardcoded schema definition.

▶️ Running the Application

Start Streamlit:

streamlit run app.py

The application will open in the browser.

You can then enter a natural-language question.

Example:

What is the average salary of each department?

The application will display:

Generated SQL
AI explanation
Query results
Visualization when applicable
Number of execution attempts
🧪 Testing

The project has been tested for:

Database Connection
SELECT 1;

The MySQL connection successfully returns:

1
SQL Validation

Invalid non-SELECT queries are rejected.

Example:

DELETE FROM employees;

Result:

Only SELECT queries are allowed.
SQL Syntax Validation

Malformed SQL is detected using SQLGlot.

SQL Execution Errors

Invalid column references are detected by MySQL and passed to the SQL repair workflow.

Example:

SELECT full_name FROM employees;

can be repaired to:

SELECT name FROM employees;
Natural Language Queries

The system has been tested with:

Basic SELECT queries
JOIN queries
Aggregate queries
GROUP BY queries
HAVING queries
Ranking queries
Multi-table analytical queries
📈 Current Capabilities

The current version supports:

Natural-language database interaction
Automatic schema extraction
Gemini-powered SQL generation
SQL validation
MySQL execution
Automatic SQL error repair
AI-generated result explanations
Basic automatic visualizations
SELECT-only query protection
Relational database queries
Multi-table JOINs
Aggregations and analytical SQL
⚠️ Limitations

Although the application provides automatic SQL generation and repair, generated SQL can still be semantically incorrect while remaining syntactically valid.

For example, a query may execute successfully but interpret a business question incorrectly.

The current repair mechanism primarily handles SQL execution errors, not all forms of semantic correctness.

For production deployment, additional safeguards would be recommended, including:

Dedicated read-only database credentials
Stronger SQL AST validation
Query timeout limits
Row/result limits
Query cost controls
Better semantic validation
Logging and monitoring
Authentication and authorization
🔮 Future Improvements

Potential future improvements include:

Conversational multi-turn database queries
Query result caching
More advanced chart recommendations
Power BI / Tableau integration
Database upload and connection management
Support for PostgreSQL
Support for SQLite
Query performance analysis
SQL query optimization
Better semantic SQL validation
User authentication
Query execution limits
Production-grade read-only database access
More advanced data visualizations
🎯 Project Goal

The goal of this project is to make relational databases easier to interact with by allowing users to ask analytical questions using natural language.

The project combines:

Natural Language Processing
        +
Large Language Models
        +
SQL
        +
Relational Databases
        +
Data Analytics
        +
Data Visualization

This makes the system useful as an AI-powered SQL analytics assistant for users who may not be comfortable writing SQL manually.

👨‍💻 Author

Prince Meena

AI / Software Engineering Enthusiast

⭐ Project Highlights
Built an end-to-end AI-powered Text-to-SQL system
Integrated Gemini with a relational MySQL database
Implemented automatic schema-aware SQL generation
Added SQL validation using SQLGlot
Implemented automatic SQL error repair
Added AI-powered result explanations
Added automatic result visualization
Designed the system around relational database relationships and analytical SQL