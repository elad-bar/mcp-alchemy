from datetime import datetime, date
import json

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
        logger.debug(f"Schema definitions: {all_schema_response}")

        return all_schema_response

    def get_execute_query_response(self, query, params):
        query = self._request_context.get_parameter("query", query)
        params = self._request_context.get_parameter("params", params)
            
        result = {
            "query": query,
            "params": params
        }

        execute_query_max_chars = self._request_context.execute_query_max_chars

        try:
            logger.info(f"Executing query '{query}', params: {params}")

            cursor = self._request_context.db_context.execute_query(query, params)
            
            if cursor.returns_rows:
                data = self._format_query_execution_result(cursor, execute_query_max_chars)
                
                result.update(data)

            logger.info(f"Query '{query}' executed successfully")

        except Exception as e:
            error = {
                "error": str(e),
            }
            
            result.update(error)

            logger.error(f"Error executing query '{query}', params: {params}, Error: {str(e)}")

        return result

    def _format_query_execution_result(self, cursor, execute_query_max_chars):
        """Format rows in a clean vertical format"""
        rows = []
        content_length = 0
        total_rows = 0

        while row := cursor.fetchone():
            total_rows += 1
            
            if content_length > execute_query_max_chars:
                continue
            
            row_data = {}

            for col, val in zip(cursor.keys(), row):
                row_data[col] = self._format_value(val)
                
            content_length += len(json.dumps(row_data))
                
            if content_length > execute_query_max_chars:
                continue
            
            rows.append(row_data)
            
        data = {
            "rows": rows,
            "response_rows": len(rows),
            "total_rows": total_rows,            
        }        

        return data

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
        found = data.get("found")
        columns = data.get("columns")
        foreign_keys = data.get("foreign_keys")
        primary_keys = data.get("primary_keys")

        data = {
            "table_name": table_name,
            "found": found
        }
        
        if found:
            data["columns"] = []
            data["relationships"] = []

            # Process columns
            for column in columns:
                if "comment" in column:
                    del column["comment"]

                name = column.pop("name")
                
                column_data = {
                    "name": name
                }

                if name in primary_keys:
                    column_data["primary_key"] = True

                column_data["type"] = str(column.pop("type"))
                
                for key, value in column.items():
                    if value:
                        column_data[key] = value

                data["columns"].append(column_data)

            # Process relationships
            if foreign_keys:
                data["relationships"] = [
                    {
                        "constrained_columns": fk['constrained_columns'],
                        "referred_table": fk['referred_table'],
                        "referred_columns": fk['referred_columns']
                    }
                    for fk in foreign_keys
                ]

        return data
