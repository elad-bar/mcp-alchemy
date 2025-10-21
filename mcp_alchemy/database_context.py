import time

from mcp.server.fastmcp.utilities.logging import get_logger
from sqlalchemy import Connection, create_engine, text, inspect

logger = get_logger(__name__)

DISPOSE_UNUSED_CONNECTION_INTERVAL = 60 * 10


class DatabaseContext:
    connection: Connection | None

    def __init__(self, db_url: str, db_engine_options: dict):
        self._db_url = db_url
        self._db_engine_options = db_engine_options

        self.connection = self._get_connection()
        self.last_used = 0

    def mark_as_used(self):
        self.last_used = time.time()

    def should_close(self):
        now = time.time()

        should_close_connection = now - self.last_used >= DISPOSE_UNUSED_CONNECTION_INTERVAL

        return should_close_connection

    def _get_connection(self) -> Connection:
        try:
            logger.info(f"Creating connection to: {self._db_url}, Options: {self._db_engine_options}")

            engine = create_engine(self._db_url, **self._db_engine_options)
            connection = engine.connect()

            logger.info("Connected")

            return connection

        except Exception as ex:
            logger.error(f"Failed to get database connection, Error: {ex}")

            raise ex

    def is_connected(self):
        return self.connection and not self.connection.closed and self.connection.connection.is_valid

    def execute_query(self, query, params):
        cursor = self.connection.execute(text(query), params)

        return cursor

    def get_tables(self, filter_query: str | None = None) -> list[str]:
        inspector = inspect(self.connection)

        all_tables = inspector.get_table_names()

        filtered_tables = [
            table_name
            for table_name in all_tables
            if filter_query is None or filter_query in table_name
        ]

        return filtered_tables

    def get_schema_details(self, table_names: list[str]):
        inspector = inspect(self.connection)
        table_schema_list = []

        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            primary_keys = set(pk_constraint["constrained_columns"])

            data = {
                "name": table_name,
                "columns": columns,
                "foreign_keys": foreign_keys,
                "primary_keys": primary_keys
            }

            table_schema_list.append(data)

        return table_schema_list
