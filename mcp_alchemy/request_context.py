import hashlib
import json
import logging
import os
import threading

from time import sleep

from fastmcp import Context
from fastmcp.server.dependencies import get_http_headers

from mcp_alchemy.connection_config import (
    PARAM_DB_ENGINE_OPTIONS,
    PARAM_EXECUTE_QUERY_MAX_CHARS,
    SUPPORTED_ENV_VARS,
    SUPPORTED_HEADERS,
    merge_config,
    normalize_header_key,
    resolve_db_url,
)

__all__ = [
    "RequestContext",
    "SUPPORTED_ENV_VARS",
    "SUPPORTED_HEADERS",
]
from mcp_alchemy.database_context import DatabaseContext

logger = logging.getLogger(__name__)

DISPOSE_UNUSED_CONNECTIONS_INTERVAL = 1

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
    context: Context | None
    db_context: DatabaseContext | None

    def __init__(self, ctx: Context | None = None):
        self.context = ctx
        raw_headers = get_http_headers(include_all=True) or {}

        headers: dict[str, str] = {}
        for key, value in raw_headers.items():
            env_key = normalize_header_key(key)
            if env_key in SUPPORTED_ENV_VARS:
                headers[env_key] = value

        env = {
            key: os.environ[key]
            for key in SUPPORTED_ENV_VARS
            if key in os.environ
        }

        merged = merge_config(env, headers)

        self.db_url = resolve_db_url(merged)

        self.execute_query_max_chars = int(
            merged.get(PARAM_EXECUTE_QUERY_MAX_CHARS) or DEFAULT_EXECUTE_QUERY_MAX_CHARS
        )

        db_engine_options = merged.get(PARAM_DB_ENGINE_OPTIONS) or DEFAULT_DB_ENGINE_OPTIONS

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
            DATABASE_CONTEXT_LIST[connection_id] = db_context

        self.db_context = db_context

        self.db_context.mark_as_used()

    @staticmethod
    def header_key_to_env_var_format(key: str) -> str:
        return normalize_header_key(key)

    @staticmethod
    def load(ctx: Context | None = None):
        return RequestContext(ctx)

    @staticmethod
    def dispose_unused_connections(stop_event: threading.Event):
        while not stop_event.is_set():
            closed_connections = []
            for connection_id in DATABASE_CONTEXT_LIST:
                db_context = DATABASE_CONTEXT_LIST[connection_id]

                if db_context.should_close():
                    db_context.connection.close()
                    closed_connections.append(connection_id)

            for closed_connection in closed_connections:
                del DATABASE_CONTEXT_LIST[closed_connection]

            sleep(DISPOSE_UNUSED_CONNECTIONS_INTERVAL)



