import json
from enum import StrEnum


class MCPTool(StrEnum):
    all_table_names = "all_table_names"
    filter_table_names = "filter_table_names"
    schema_definitions = "schema_definitions"
    execute_query = "execute_query"

    def to_description(self) -> str | None:
        description: str | None = None

        if self == MCPTool.all_table_names:
            description = "Return all table names in the database separated by comma."

        elif self == MCPTool.filter_table_names:
            description = "Return all table names in the database containing the substring 'q' separated by comma."

        elif self == MCPTool.schema_definitions:
            description = "Returns schema and relation information for the given tables."

        elif self == MCPTool.execute_query:
            description = (
                "Execute a SQL query and return results in a readable format.\n"
                "Results will be truncated after characters as configured in the parameter.\n"
                "Claude Desktop may fetch the full result set via an url for analysis and artifacts (Optional - using CLAUDE_LOCAL_FILES_PATH).\n"
                "IMPORTANT: \n"
                "1. You MUST use the params parameter for query parameter substitution to prevent SQL injection.\n"
                "\tExample: 'WHERE id = :id' with params={'id': 123}\n"
                "2. Direct string concatenation is a serious security risk."
            )

        return description