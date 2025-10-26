from datetime import datetime, date

from mcp.server.fastmcp.utilities.logging import get_logger

from mcp_alchemy.request_context import RequestContext

SHOW_KEY_ONLY = {"nullable", "autoincrement"}

logger = get_logger(__name__)


class ResponseFormatter:
    _request_context: RequestContext

    def __init__(self, request_context: RequestContext):
        self._request_context = request_context

    def get_schema_list_response(self, table_names):
        table_names = self._request_context.get_parameter("table_names", table_names)

        logger.info(f"Retrieving schema definition for table names: '{table_names}'")

        table_schema_list = self._request_context.db_context.get_schema_details(table_names)

        all_schema_response = [
            self._format_single_schema_response(table_schema)
            for table_schema in table_schema_list
        ]

        logger.info(f"{len(table_schema_list):,.0f} schema definitions found for tables '{table_names}'")

        response = "\n".join(all_schema_response)

        return response

    def get_execute_query_response(self, query, params):
        query = self._request_context.get_parameter("query", query)
        params = self._request_context.get_parameter("params", params)

        execute_query_max_chars = self._request_context.execute_query_max_chars

        try:
            logger.info(f"Executing query '{query}', params: {params}")

            cursor = self._request_context.db_context.execute_query(query, params)

            if not cursor.returns_rows:
                message = f"Success: {cursor.rowcount} rows affected"

            else:
                output = self._format_query_execution_result(cursor, execute_query_max_chars)
                message = "\n".join(output)

            logger.info(message)

            return message

        except Exception as e:
            message = f"Error: {str(e)}"

            logger.error(message)

            return message

    def _format_query_execution_result(self, cursor, execute_query_max_chars):
        """Format rows in a clean vertical format"""
        output = []
        size, i, did_truncate = 0, 0, False

        i = 0
        while row := cursor.fetchone():
            i += 1

            if did_truncate:
                continue

            sub_result = [f"{i}. row"]

            for col, val in zip(cursor.keys(), row):
                sub_result.append(f"{col}: {self._format_value(val)}")

            sub_result.append("")

            size += sum(len(x) + 1 for x in sub_result)  # +1 is for line endings

            if size > execute_query_max_chars:
                did_truncate = True
                break
            else:
                output.extend(sub_result)

        if i == 0:
            return ["No rows returned"]

        elif did_truncate:
            output.append(f"Result: showing first {i - 1} rows (output truncated)")

            return output

        else:
            output.append(f"Result: {i} rows")

            return output

    @staticmethod
    def _format_value(val) -> str:
        """Format a value for display, handling None and datetime types"""
        if val is None:
            return "NULL"
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        return str(val)

    @staticmethod
    def _format_single_schema_response(data: dict):
        table_name = data.get("name")
        columns = data.get("columns")
        foreign_keys = data.get("foreign_keys")
        primary_keys = data.get("primary_keys")

        result = [f"{table_name}:"]

        # Process columns
        for column in columns:
            if "comment" in column:
                del column["comment"]

            name = column.pop("name")

            column_parts = []

            if name in primary_keys:
                column_parts.append("primary key")

            column_parts.append(str(column.pop("type")))

            for key, value in column.items():
                if value:
                    if key in SHOW_KEY_ONLY:
                        column_parts.append(key)

                    else:
                        column_parts.append(f"{key}={value}")

            column_parts_str = ", ".join(column_parts)

            result.append(f"    {name}: {column_parts_str}")

        # Process relationships
        if foreign_keys:
            result.extend(["", "    Relationships:"])

            for fk in foreign_keys:
                constrained_columns = fk['constrained_columns']
                referred_table = fk['referred_table']
                referred_columns = fk['referred_columns']

                constrained_columns_str = ", ".join(constrained_columns)
                referred_columns_str = ", ".join(referred_columns)

                result.append(f"      {constrained_columns_str} -> {referred_table}.{referred_columns_str}")

        return "\n".join(result)
