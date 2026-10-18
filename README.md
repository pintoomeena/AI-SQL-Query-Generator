🗄️ AI SQL Query Generator
An AI-powered Text-to-SQL analytics assistant that lets users query a relational database using natural language. The application uses Google Gemini to generate SQL, validates the query, executes it against the connected database, explains the results, and creates basic visualizations.
Instead of manually writing SQL, users can ask questions such as:
- Show me all employees
- What is the average salary of each department?
- Which department has the highest average salary?
- Which employees are working on more than one project?
The application uses Google Gemini to convert natural-language questions into SQL, validates the generated query, executes it against the configured database, attempts to repair execution errors, explains the results, and generates basic visualizations.
Live demo: https://ai-sql-query-generator-6zhp.onrender.com
GitHub: https://github.com/pintoomeena/AI-SQL-Query-Generator
🚀 Features
1. Natural Language → SQL
Users can ask database questions in plain English.
Example:
Which department has the highest average salary?

Generated SQL:
SELECT d.name, AVG(e.salary) AS average_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY average_salary DESC
LIMIT 1;
2. Automatic Database Schema Extraction
The application dynamically extracts the connected database schema using SQLAlchemy. Production uses Neon PostgreSQL through DATABASE_URL; local development can use MySQL.
It identifies:
- Tables
- Columns
- Data types
- Primary keys
- Foreign keys
- Table relationships
The extracted schema is provided to Gemini to improve SQL generation accuracy.
3. SQL Validation
Generated SQL is validated using SQLGlot before execution.
The system checks:
- SQL syntax
- Single-statement execution
- SELECT-only queries
For example, non-read queries such as:
DELETE FROM employees;
are rejected.
4. SQL Execution
Validated queries are executed against the configured database using SQLAlchemy (Neon PostgreSQL in production, or MySQL for local development).
Results are displayed in a structured Streamlit table.
5. Automatic SQL Error Repair
If generated SQL fails during execution, the system sends the following information back to Gemini:
- User question
- Database schema
- Generated SQL
- Database execution error
Gemini then generates a corrected query and the system retries execution.
Example:
Generated SQL:
SELECT full_name FROM employees;
MySQL error:
Unknown column 'full_name' in 'field list'
Corrected SQL:
SELECT name FROM employees;
6. AI Result Explanation
After successful execution, Gemini generates a concise natural-language explanation of the result.
7. Data Visualization
When the returned data contains suitable numeric and categorical columns, the application automatically generates a basic visualization.
For example:
What is the average salary of each department?

The application can display department-wise salary averages together with a bar chart.
8. Read-Only Query Protection
The current application allows only SELECT queries through SQL validation.
This blocks queries such as:
INSERT
UPDATE
DELETE
DROP
ALTER
Production note: A production deployment should also use dedicated read-only database credentials and stronger database-level restrictions.

Application-level SQL validation is a useful safeguard, but it is not a complete security boundary. For production, use a dedicated database account with read-only permissions and least-privilege access. Consider query timeouts, result-size limits, authentication, rate limiting, monitoring, and audit logging before exposing the application to untrusted users.
🏗️ Architecture
                    ┌─────────────────────┐
                    │        User         │
                    │  Natural Language   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Query Service    │
                    │   Workflow Manager  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
     ┌─────────────────────┐       ┌─────────────────────┐
     │   Schema Service    │       │    LLM Service      │
     │                     │       │                     │
     │ • Tables            │──────▶│ • Gemini            │
     │ • Columns           │       │ • Natural Language  │
     │ • PKs / FKs         │       │   → SQL             │
     └─────────────────────┘       └──────────┬──────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │     SQL Service     │
                                   │                     │
                                   │ • Clean SQL         │
                                   │ • Validate SQL      │
                                   │ • Execute SQL       │
                                   └──────────┬──────────┘
                                              │
                                     ┌────────┴────────┐
                                     │                 │
                                  Success            Error
                                     │                 │
                                     ▼                 ▼
                              ┌──────────────┐  ┌──────────────┐
                              │ Query Result │  │ SQL Repair   │
                              │              │  │ via Gemini   │
                              └──────┬───────┘  └──────┬───────┘
                                     │                 │
                                     └────────┬────────┘
                                              ▼
                                   ┌─────────────────────┐
                                   │ Results + AI        │
                                   │ Explanation + Chart │
                                   └─────────────────────┘
🗃️ Database Schema
The sample relational database contains six related tables. The production deployment uses Neon PostgreSQL; the local Docker Compose setup can use MySQL.
departments
Column	Description
id	Primary key
name	Department name
location	Department location


employees
Column	Description
id	Primary key
name	Employee name
email	Employee email
job_title	Employee role
salary	Current salary
department_id	Foreign key to departments.id
joining_date	Joining date
manager_id	Self-referencing employee manager


projects
Column	Description
id	Primary key
name	Project name
budget	Project budget
status	Project status
start_date	Project start date
end_date	Project end date


employee_projects
Many-to-many relationship between employees and projects.
Column	Description
employee_id	Foreign key to employees.id
project_id	Foreign key to projects.id
role	Employee's project role
assigned_date	Assignment date


performance_reviews
Column	Description
id	Primary key
employee_id	Foreign key to employees.id
review_date	Review date
rating	Performance rating
comments	Review comments


salaries
Stores historical salary records.
Column	Description
id	Primary key
employee_id	Foreign key to employees.id
salary	Salary amount
effective_from	Effective date


🔗 Database Relationships
departments
     │
     │ 1:N
     ▼
employees
     │
     ├───────────────┐
     │               │
     │               ▼
     │        performance_reviews
     │
     ├───────────────┐
     │               │
     │               ▼
     │           salaries
     │
     ▼
employee_projects
     │
     │ N:1
     ▼
projects
Key Relationships
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
User Question
      │
      ▼
Extract Database Schema
      │
      ▼
Question + Schema → Gemini
      │
      ▼
Generate SQL
      │
      ▼
Clean SQL
      │
      ▼
Validate SQL
      │
      ▼
Execute SQL
      │
      ├───────────────┐
      │               │
   Success           Error
      │               │
      ▼               ▼
   Results       Gemini SQL Repair
      │               │
      ▼               ▼
AI Explanation      Retry
      │
      ▼
Visualization
🔄 SQL Repair Loop
The application supports automatic repair of SQL execution errors.
Generated SQL
      │
      ▼
Execute Query
      │
      ├───────────────┐
      │               │
   Success           Error
      │               │
      ▼               ▼
   Return       Send error + schema
   Results          to Gemini
                      │
                      ▼
                Correct SQL
                      │
                      ▼
                  Retry Query
The system supports a limited number of repair attempts to avoid unnecessary API usage.
📊 Example Queries
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
Which employees have a performance rating above 4
and are working on more than one project?

Which department has the highest average employee salary?

Which projects have more than two employees assigned?
🛠️ Tech Stack
Category	Technology
Frontend	Streamlit
Backend	Python
LLM	Google Gemini API (google-genai)
SQL validation	SQLGlot
Database connectivity	SQLAlchemy
Production database	Neon PostgreSQL
Local database	MySQL 8, PyMySQL
PostgreSQL driver	psycopg[binary]
Configuration	python-dotenv
Containerization	Docker, Docker Compose
CI/CD	GitHub Actions
Container security scanning	Trivy
Hosting	Render


📁 Project Structure
AI_SQL_QUERY_GENERATOR/
│
├── app.py
├── README.md
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
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
venv/ and .env are excluded from Git using .gitignore.

⚙️ Installation
1. Clone the Repository
git clone https://github.com/pintoomeena/AI-SQL-Query-Generator.git
cd AI-SQL-Query-Generator
2. Create a Virtual Environment
python -m venv venv
Activate it on Windows:
.\venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables
Create a .env file in the project root:
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=temp

# For production / Neon PostgreSQL, configure DATABASE_URL instead:
# DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require

GEMINI_API_KEY=your_gemini_api_key
Never commit your actual .env file or API key to GitHub.
The repository includes .env.example as a safe template.
🗄️ Database Setup
Create the MySQL database:
CREATE DATABASE temp;
Create and populate the following tables:
departments
employees
projects
employee_projects
performance_reviews
salaries
The application dynamically extracts the database schema, so the schema does not need to be hardcoded inside the SQL-generation logic.
▶️ Running the Application
Start the Streamlit application:
streamlit run app.py
Then open the local URL displayed by Streamlit in your browser.
Example question:
What is the average salary of each department?
The application displays:
1. Generated SQL
2. AI explanation
3. Query results
4. Visualization when applicable
5. Number of execution attempts
🚀 Deployment
The application is deployed on Render and uses Neon PostgreSQL in production.
Configure these environment variables in Render:
- DATABASE_URL — the Neon PostgreSQL connection string.
- GEMINI_API_KEY — the Google Gemini API key.
Keep credentials in Render's environment settings; never hardcode them in source code or commit them to GitHub. After pushing code changes, deploy the latest commit from the Render dashboard and inspect the build/runtime logs if startup fails.
Local Docker Compose
Build and start the local application and database services:
docker compose up --build
Open the Streamlit URL shown by Docker, usually http://localhost:8501.
GitHub Actions and DevOps
The repository's CI workflow includes automated tests, Python syntax checks, Docker image build verification, and Trivy vulnerability scanning. Check .github/workflows/ for the exact triggers and configuration in the current branch. A successful CI run confirms that configured checks passed; it does not guarantee every production integration will work.
Database migration
A migration script was used to transfer the MySQL schema and data to Neon PostgreSQL. The migration was verified by comparing row counts across six tables. Do not run the migration script again against an already-populated production database unless you deliberately intend to perform another migration and have reviewed its behavior.
🧪 Testing
The project has been tested for:
Database Connection
SELECT 1;
Verifies connectivity to whichever database is configured.
SQL Validation
Non-SELECT queries are rejected.
DELETE FROM employees;
Expected behavior:
Only SELECT queries are allowed.
SQL Syntax Validation
Malformed SQL is detected using SQLGlot before execution.
SQL Execution Errors
Invalid column references are detected by the connected database and passed to the SQL repair workflow.
Example:
SELECT full_name FROM employees;
can be corrected to:
SELECT name FROM employees;
Natural Language Queries
Tested query categories include:
- Basic SELECT
- JOIN
- Aggregation
- GROUP BY
- HAVING
- Ranking
- Multi-table analytical queries
📈 Current Capabilities
- Natural-language database interaction
- Automatic database schema extraction
- Gemini-powered SQL generation
- SQL syntax validation
- Query execution against PostgreSQL in production and MySQL locally
- Automatic SQL error repair
- AI-generated result explanations
- Basic automatic visualizations
- SELECT-only query protection
- Relational database queries
- Multi-table JOINs
- Aggregations and analytical SQL
⚠️ Limitations
The application can generate SQL that is syntactically valid but semantically incorrect.
For example, a query may execute successfully while still interpreting a business question incorrectly.
The current repair mechanism primarily handles SQL execution errors, not every form of semantic error.
For production deployment, additional safeguards would be recommended:
- Dedicated read-only database credentials
- Stronger SQL AST validation
- Query timeout limits
- Result-size limits
- Query cost controls
- Semantic validation
- Logging and monitoring
- Authentication and authorization
🧰 Troubleshooting
Issue	What to check
PostgreSQL driver/import error	Confirm psycopg[binary] is in requirements.txt and rebuild/redeploy.
Production tries to connect to MySQL	Confirm DATABASE_URL is set in Render and the latest code is deployed.
Database connection error	Check the Neon connection string, SSL settings, and database availability.
Gemini API error	Check GEMINI_API_KEY, API access, model availability, and usage limits.
Render appears to run old code	Verify the deployed commit and use Manual Deploy → Deploy latest commit after pushing changes.


🔮 Future Improvements
- Conversational multi-turn database queries
- Query result caching
- Improved chart recommendations
- Power BI / Tableau integration
- Database connection management
- Additional database engines and connection management
- SQLite support
- Query performance analysis
- SQL query optimization
- Improved semantic SQL validation
- User authentication
- Query execution limits
- Production-grade read-only database access
- Advanced data visualizations
🎯 Project Goal
The goal of this project is to make relational databases easier to interact with by allowing users to ask analytical questions using natural language.
The project combines:
Natural Language
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
⭐ Project Highlights
- Built an end-to-end AI-powered Text-to-SQL system
- Integrated Gemini with a relational database, using Neon PostgreSQL in production and MySQL locally
- Implemented schema-aware SQL generation
- Added SQL validation using SQLGlot
- Implemented automatic SQL error repair
- Added AI-powered result explanations
- Added automatic result visualization
- Designed the system around relational database relationships and analytical SQL
👨‍💻 Author
Pintoo Meena
AI / Software Engineering Enthusiast
🔗 Repository
GitHub Repository
