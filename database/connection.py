
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if database_url:
    # Render / Neon PostgreSQL
    connection_url = make_url(database_url)

    if connection_url.drivername == "postgresql":
        connection_url = connection_url.set(
            drivername="postgresql+psycopg"
        )

    engine = create_engine(connection_url, pool_pre_ping=True)

else:
    # Local MySQL / Docker Compose
    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
    )

    engine = create_engine(connection_url, pool_pre_ping=True)


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            print("Result:", result.scalar())

    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)


if __name__ == "__main__":
    test_connection()
