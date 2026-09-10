# 🗄️ AI SQL Query Generator

An AI-powered SQL analytics assistant that allows users to interact with a relational MySQL database using natural language.

Instead of manually writing SQL, users can ask questions such as:

- **Show me all employees**
- **What is the average salary of each department?**
- **Which department has the highest average salary?**
- **Which employees are working on more than one project?**

The application uses **Google Gemini** to convert natural-language questions into SQL, validates the generated query, executes it against MySQL, automatically repairs execution errors, explains the results, and generates basic visualizations.

---

## 🚀 Features

### 1. Natural Language → SQL

Users can ask database questions in plain English.

**Example:**

> Which department has the highest average salary?

Generated SQL:

```sql
SELECT d.name, AVG(e.salary) AS average_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY average_salary DESC
LIMIT 1;
```

### 2. Automatic Database Schema Extraction

The application dynamically extracts the MySQL schema using SQLAlchemy.

It identifies:

- Tables
- Columns
- Data types
- Primary keys
- Foreign keys
- Table relationships

The extracted schema is provided to Gemini to improve SQL generation accuracy.

### 3. SQL Validation

Generated SQL is validated using **SQLGlot** before execution.

The system checks:

- SQL syntax
- Single-statement execution
- `SELECT`-only queries

For example, non-read queries such as:

```sql
DELETE FROM employees;
```

are rejected.

### 4. SQL Execution

Validated queries are executed against MySQL using **SQLAlchemy**.

Results are displayed in a structured Streamlit table.

### 5. Automatic SQL Error Repair

If generated SQL fails during execution, the system sends the following information back to Gemini:

- User question
- Database schema
- Generated SQL
- MySQL error

Gemini then generates a corrected query and the system retries execution.

**Example:**

Generated SQL:

```sql
SELECT full_name FROM employees;
```

MySQL error:

```text
Unknown column 'full_name' in 'field list'
```

Corrected SQL:

```sql
SELECT name FROM employees;
```

### 6. AI Result Explanation

After successful execution, Gemini generates a concise natural-language explanation of the result.

### 7. Data Visualization

When the returned data contains suitable numeric and categorical columns, the application automatically generates a basic visualization.

For example:

> What is the average salary of each department?

The application can display department-wise salary averages together with a bar chart.

### 8. Read-Only Query Protection

The current application allows only `SELECT` queries through SQL validation.

This blocks queries such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
```

> **Production note:** A production deployment should also use dedicated read-only database credentials and stronger database-level restrictions.

---

## 🏗️ Architecture

```text
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
                              │ MySQL Result │  │ SQL Repair   │
                              │              │  │ via Gemini   │
                              └──────┬───────┘  └──────┬───────┘
                                     │                 │
                                     └────────┬────────┘
                                              ▼
                                   ┌─────────────────────┐
                                   │ Results + AI        │
                                   │ Explanation + Chart │
                                   └─────────────────────┘
```

---

## 🗃️ Database Schema

The project uses a relational MySQL database containing six related tables.

### `departments`

| Column | Description |
|---|---|
| `id` | Primary key |
| `name` | Department name |
| `location` | Department location |

### `employees`

| Column | Description |
|---|---|
| `id` | Primary key |
| `name` | Employee name |
| `email` | Employee email |
| `job_title` | Employee role |
| `salary` | Current salary |
| `department_id` | Foreign key to `departments.id` |
| `joining_date` | Joining date |
| `manager_id` | Self-referencing employee manager |

### `projects`

| Column | Description |
|---|---|
| `id` | Primary key |
| `name` | Project name |
| `budget` | Project budget |
| `status` | Project status |
| `start_date` | Project start date |
| `end_date` | Project end date |

### `employee_projects`

Many-to-many relationship between employees and projects.

| Column | Description |
|---|---|
| `employee_id` | Foreign key to `employees.id` |
| `project_id` | Foreign key to `projects.id` |
| `role` | Employee's project role |
| `assigned_date` | Assignment date |

### `performance_reviews`

| Column | Description |
|---|---|
| `id` | Primary key |
| `employee_id` | Foreign key to `employees.id` |
| `review_date` | Review date |
| `rating` | Performance rating |
| `comments` | Review comments |

### `salaries`

Stores historical salary records.

| Column | Description |
|---|---|
| `id` | Primary key |
| `employee_id` | Foreign key to `employees.id` |
| `salary` | Salary amount |
| `effective_from` | Effective date |

---

## 🔗 Database Relationships

```text
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
```

### Key Relationships

```text
employees.department_id
        ↓
departments.id
```

```text
employee_projects.employee_id
        ↓
employees.id
```

```text
employee_projects.project_id
        ↓
projects.id
```

```text
performance_reviews.employee_id
        ↓
employees.id
```

```text
salaries.employee_id
        ↓
employees.id
```

---

## 🤖 AI Workflow

```text
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
```

---

## 🔄 SQL Repair Loop

The application supports automatic repair of SQL execution errors.

```text
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
```

The system supports a limited number of repair attempts to avoid unnecessary API usage.

---

## 📊 Example Queries

### Basic Queries

```text
Show me all employees
Show all projects
List all departments
```

### Filtering

```text
Show employees with salary greater than 100000
Show employees who joined after 2023
```

### Aggregation

```text
What is the average salary of each department?
What is the total salary paid by each department?
How many employees are in each department?
```

### Ranking

```text
Which department has the highest average salary?
Who is the highest paid employee?
Which project has the highest budget?
```

### JOIN Queries

```text
Show employees along with their department names
Show employees working on each project
Show employee names and their performance ratings
```

### Complex Analytical Queries

```text
Which employees have a performance rating above 4
and are working on more than one project?

Which department has the highest average employee salary?

Which projects have more than two employees assigned?
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Database | MySQL 8 |
| Database Connectivity | SQLAlchemy, PyMySQL |
| AI | Google Gemini API |
| AI SDK | `google-genai` |
| SQL Processing | SQLGlot |
| Configuration | `python-dotenv` |

---

## 📁 Project Structure

```text
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
```

> `venv/` and `.env` are excluded from Git using `.gitignore`.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pintoomeena/AI-SQL-Query-Generator.git
cd AI-SQL-Query-Generator
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=temp

GEMINI_API_KEY=your_gemini_api_key
```

**Never commit your actual `.env` file or API key to GitHub.**

The repository includes `.env.example` as a safe template.

---

## 🗄️ Database Setup

Create the MySQL database:

```sql
CREATE DATABASE temp;
```

Create and populate the following tables:

```text
departments
employees
projects
employee_projects
performance_reviews
salaries
```

The application dynamically extracts the database schema, so the schema does not need to be hardcoded inside the SQL-generation logic.

---

## ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open the local URL displayed by Streamlit in your browser.

Example question:

```text
What is the average salary of each department?
```

The application displays:

1. Generated SQL
2. AI explanation
3. Query results
4. Visualization when applicable
5. Number of execution attempts

---

## 🧪 Testing

The project has been tested for:

### Database Connection

```sql
SELECT 1;
```

Successfully verifies the MySQL connection.

### SQL Validation

Non-`SELECT` queries are rejected.

```sql
DELETE FROM employees;
```

Expected behavior:

```text
Only SELECT queries are allowed.
```

### SQL Syntax Validation

Malformed SQL is detected using SQLGlot before execution.

### SQL Execution Errors

Invalid column references are detected by MySQL and passed to the SQL repair workflow.

Example:

```sql
SELECT full_name FROM employees;
```

can be corrected to:

```sql
SELECT name FROM employees;
```

### Natural Language Queries

Tested query categories include:

- Basic `SELECT`
- `JOIN`
- Aggregation
- `GROUP BY`
- `HAVING`
- Ranking
- Multi-table analytical queries

---

## 📈 Current Capabilities

- Natural-language database interaction
- Automatic database schema extraction
- Gemini-powered SQL generation
- SQL syntax validation
- MySQL query execution
- Automatic SQL error repair
- AI-generated result explanations
- Basic automatic visualizations
- `SELECT`-only query protection
- Relational database queries
- Multi-table `JOIN`s
- Aggregations and analytical SQL

---

## ⚠️ Limitations

The application can generate SQL that is syntactically valid but semantically incorrect.

For example, a query may execute successfully while still interpreting a business question incorrectly.

The current repair mechanism primarily handles **SQL execution errors**, not every form of semantic error.

For production deployment, additional safeguards would be recommended:

- Dedicated read-only database credentials
- Stronger SQL AST validation
- Query timeout limits
- Result-size limits
- Query cost controls
- Semantic validation
- Logging and monitoring
- Authentication and authorization

---

## 🔮 Future Improvements

- Conversational multi-turn database queries
- Query result caching
- Improved chart recommendations
- Power BI / Tableau integration
- Database connection management
- PostgreSQL support
- SQLite support
- Query performance analysis
- SQL query optimization
- Improved semantic SQL validation
- User authentication
- Query execution limits
- Production-grade read-only database access
- Advanced data visualizations

---

## 🎯 Project Goal

The goal of this project is to make relational databases easier to interact with by allowing users to ask analytical questions using natural language.

The project combines:

```text
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
```

This makes the system useful as an **AI-powered SQL analytics assistant** for users who may not be comfortable writing SQL manually.

---

## ⭐ Project Highlights

- Built an end-to-end AI-powered Text-to-SQL system
- Integrated Gemini with a relational MySQL database
- Implemented schema-aware SQL generation
- Added SQL validation using SQLGlot
- Implemented automatic SQL error repair
- Added AI-powered result explanations
- Added automatic result visualization
- Designed the system around relational database relationships and analytical SQL

---

## 👨‍💻 Author

**Pintoo Meena**

AI / Software Engineering Enthusiast

---

## 🔗 Repository

[GitHub Repository](https://github.com/pintoomeena/AI-SQL-Query-Generator)
