
import pytest

from services.sql_service import validate_sql


def test_valid_select_query():
    sql = "SELECT name FROM employees"
    assert validate_sql(sql) == sql


def test_select_query_with_where():
    sql = "SELECT name FROM employees WHERE department_id = 1"
    assert validate_sql(sql) == sql


def test_sql_with_markdown_code_block():
    sql = "```sql\nSELECT name FROM employees\n```"
    assert validate_sql(sql) == "SELECT name FROM employees"


def test_empty_sql_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        validate_sql("")


def test_insert_query_is_rejected():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("INSERT INTO employees (name) VALUES ('Test')")


def test_delete_query_is_rejected():
    with pytest.raises(ValueError, match="Only SELECT"):
        validate_sql("DELETE FROM employees")


def test_multiple_statements_are_rejected():
    with pytest.raises(ValueError, match="one SQL statement"):
        validate_sql("SELECT 1; SELECT 2")


def test_invalid_sql_syntax_is_rejected():
    with pytest.raises(ValueError, match="Invalid SQL syntax"):
        validate_sql("SELECT * FROM employees WHERE (")

