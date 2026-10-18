
import os

from sqlalchemy import (
    MetaData,
    create_engine,
    inspect,
    select,
    text,
    func,
)
from sqlalchemy.engine import URL, make_url


TABLES = [
    "departments",
    "projects",
    "employees",
    "employee_projects",
    "performance_reviews",
    "salaries",
]


def make_mysql_engine():
    required = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise RuntimeError(
            f"Missing MySQL environment variables: {missing}"
        )

    url = URL.create(
        drivername="mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
    )

    return create_engine(url, pool_pre_ping=True)


def make_postgres_engine():
    value = os.getenv("DATABASE_URL")

    if not value:
        raise RuntimeError("DATABASE_URL is missing.")

    url = make_url(value)

    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")

    if url.drivername != "postgresql+psycopg":
        raise RuntimeError(
            "DATABASE_URL must use PostgreSQL with psycopg."
        )

    return create_engine(url, pool_pre_ping=True)


def main():
    mysql = make_mysql_engine()
    pg = make_postgres_engine()

    try:
        source_inspector = inspect(mysql)
        target_inspector = inspect(pg)

        missing = set(TABLES) - set(
            source_inspector.get_table_names()
        )

        if missing:
            raise RuntimeError(
                f"Missing MySQL tables: {sorted(missing)}"
            )

        existing = target_inspector.get_table_names(
            schema="public"
        )

        if existing:
            raise RuntimeError(
                f"Neon public schema is not empty: {existing}. "
                "Migration stopped without overwriting tables."
            )

        # Reflect the existing MySQL schema.
        metadata = MetaData()
        metadata.reflect(bind=mysql, only=TABLES)

        # PostgreSQL requires index names to be unique within a schema.
        # MySQL permits the same index name on different tables.
        for table in metadata.tables.values():
            used_names = set()

            for index in table.indexes:
                old_name = index.name or "index"
                new_name = f"ix_{table.name}_{old_name}"[:63]

                if new_name in used_names:
                    raise RuntimeError(
                        f"Duplicate index name after renaming: "
                        f"{table.name}.{new_name}"
                    )

                index.name = new_name
                used_names.add(new_name)

        expected_counts = {}

        copy_order = [
            "departments",
            "projects",
            "employees",
            "employee_projects",
            "performance_reviews",
            "salaries",
        ]

        # PostgreSQL supports transactional DDL. If schema creation,
        # data insertion, sequence setup or verification fails,
        # this transaction rolls back the changes.
        with pg.begin() as destination:
            metadata.create_all(destination)
            print("PostgreSQL schema created.")

            for name in copy_order:
                table = metadata.tables[name]

                with mysql.connect() as origin:
                    rows = origin.execute(
                        select(table)
                    ).mappings().all()

                expected_counts[name] = len(rows)

                if rows:
                    destination.execute(
                        table.insert(),
                        [dict(row) for row in rows],
                    )

                print(f"{name}: copied {len(rows)} rows")

            # Reset PostgreSQL sequences for auto-increment ID columns.
            for name in TABLES:
                table = metadata.tables[name]
                primary_keys = list(table.primary_key.columns)

                if len(primary_keys) != 1:
                    continue

                column = primary_keys[0]

                if column.name != "id":
                    continue

                sequence = destination.execute(
                    text(
                        "SELECT pg_get_serial_sequence("
                        ":table_name, :column_name)"
                    ),
                    {
                        "table_name": f"public.{name}",
                        "column_name": "id",
                    },
                ).scalar_one_or_none()

                max_id = destination.execute(
                    text(f'SELECT MAX(id) FROM public."{name}"')
                ).scalar_one()

                if sequence and max_id is not None:
                    destination.execute(
                        text(
                            "SELECT setval("
                            "CAST(:sequence AS regclass), "
                            ":max_id, true)"
                        ),
                        {
                            "sequence": sequence,
                            "max_id": max_id,
                        },
                    )

            # Verify counts before committing the transaction.
            for name in TABLES:
                table = metadata.tables[name]

                actual_count = destination.execute(
                    select(func.count()).select_from(table)
                ).scalar_one()

                expected_count = expected_counts[name]

                print(
                    f"{name}: MySQL={expected_count}, "
                    f"Neon={actual_count}"
                )

                if actual_count != expected_count:
                    raise RuntimeError(
                        f"Row count mismatch for {name}. "
                        "Transaction will be rolled back."
                    )

        print("\nMigration completed successfully.")
        print("All six tables passed row-count verification.")

    finally:
        mysql.dispose()
        pg.dispose()


if __name__ == "__main__":
    main()
