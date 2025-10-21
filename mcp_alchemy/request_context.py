import hashlib
import json
import os
from time import sleep
from typing import Any

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.utilities.logging import get_logger
from starlette.requests import Request

from mcp_alchemy.database_context import DatabaseContext

logger = get_logger(__name__)

DISPOSE_UNUSED_CONNECTIONS_INTERVAL = 60

PARAM_DB_URL = "DB_URL"
PARAM_DB_ENGINE_OPTIONS = "DB_ENGINE_OPTIONS"
PARAM_EXECUTE_QUERY_MAX_CHARS = "EXECUTE_QUERY_MAX_CHARS"
PARAM_CLAUDE_LOCAL_FILES_PATH = "CLAUDE_LOCAL_FILES_PATH"

SUPPORTED_ENV_VARS = [
    PARAM_DB_URL,
    PARAM_DB_ENGINE_OPTIONS,
    PARAM_EXECUTE_QUERY_MAX_CHARS,
    PARAM_CLAUDE_LOCAL_FILES_PATH
]

SUPPORTED_HEADERS = {
    f"x-{env_var.replace('_', '-')}".lower(): env_var
    for env_var in SUPPORTED_ENV_VARS
}

DEFAULT_DB_ENGINE_OPTIONS = "{}"
DEFAULT_EXECUTE_QUERY_MAX_CHARS = "4000"

DEFAULT_OPTIONS = {
    'isolation_level': 'AUTOCOMMIT',
    # Test connections before use (handles MySQL 8hr timeout, network drops)
    'pool_pre_ping': True,
    # Keep minimal connections (MCP typically handles one request at a time)
    'pool_size': 1,
    # Allow temporary burst capacity for edge cases
    'max_overflow': 2,
    # Force refresh connections older than 1hr (well under MySQL's 8hr default)
    'pool_recycle': 3600
}

DATABASE_CONTEXT_LIST: dict[str, DatabaseContext] = {}


class RequestContext:
    db_url: str
    db_engine_options: dict
    execute_query_max_chars: int
    claude_local_files_path: str | None
    request: Request | None
    context: Context | None
    db_context: DatabaseContext | None

    def __init__(self, ctx: Context | None = None):
        self.context = ctx
        self.request = ctx.request_context.request if ctx and ctx.request_context else None

        if self.request is None:
            data = {
                str(key).upper(): os.environ[key]
                for key in os.environ
            }

        else:
            data = {
                self.header_key_to_env_var_format(key): self.request.headers[key]
                for key in self.request.headers
            }

        self.db_url = data.get(PARAM_DB_URL)

        if self.db_url is None:
            raise ValueError("DB_URL cannot be None")

        self.execute_query_max_chars = int(data.get(PARAM_EXECUTE_QUERY_MAX_CHARS, DEFAULT_EXECUTE_QUERY_MAX_CHARS))
        self.claude_local_files_path = data.get(PARAM_CLAUDE_LOCAL_FILES_PATH)

        db_engine_options = data.get(PARAM_DB_ENGINE_OPTIONS, DEFAULT_DB_ENGINE_OPTIONS)

        user_options = json.loads(db_engine_options)

        db_options = DEFAULT_OPTIONS.copy()
        db_options.update(user_options)

        self.db_engine_options = db_options

        connection_id = str(hashlib.md5(self.db_url.encode()).hexdigest())

        db_context: DatabaseContext | None = None

        if connection_id in DATABASE_CONTEXT_LIST:
            db_context = DATABASE_CONTEXT_LIST[connection_id]

        if db_context is None or not db_context.is_connected():
            db_context = DatabaseContext(self.db_url, self.db_engine_options)

        self.db_context = db_context

        self.db_context.mark_as_used()

    @staticmethod
    def header_key_to_env_var_format(key: str) -> str:
        key = key.lower()

        if key.startswith("x-"):
            key  = SUPPORTED_HEADERS.get(key)

        return key.upper()

    def get_parameter(self, key: str, value: Any | None):
        if self.request is not None:
            if value is None:
                value = self.request.query_params.get(key)

            if value is None:
                value = self.request.headers.get(key)

        return value

    @staticmethod
    def load(ctx: Context | None = None):
        return RequestContext(ctx)

    @staticmethod
    def dispose_unused_connections():
        while True:
            closed_connections = []
            for connection_id in DATABASE_CONTEXT_LIST:
                db_context = DATABASE_CONTEXT_LIST[connection_id]

                if db_context.should_close():
                    db_context.connection.close()
                    closed_connections.append(connection_id)

            for closed_connection in closed_connections:
                del DATABASE_CONTEXT_LIST[closed_connection]

            sleep(DISPOSE_UNUSED_CONNECTIONS_INTERVAL)




