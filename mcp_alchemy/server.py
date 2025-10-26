import asyncio
import os
import signal
import threading

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.utilities.logging import get_logger

from mcp_alchemy.mcp_args import MCPServerArguments
from mcp_alchemy.mcp_tools import MCPTool
from mcp_alchemy.request_context import RequestContext, SUPPORTED_HEADERS, SUPPORTED_ENV_VARS
from mcp_alchemy.response_formatter import ResponseFormatter

def tests_set_global(k, v):
    globals()[k] = v

VERSION = "2025.10.21.94000"

logger = get_logger(__name__)

IS_ENTRYPOINT = __name__ == "__main__"

ARGS = MCPServerArguments.load(IS_ENTRYPOINT)

mcp = FastMCP(ARGS.name, host=ARGS.host, port=ARGS.port, debug=ARGS.debug, stateless_http=ARGS.stateless_http)

logger.info(f"Starting MCP Alchemy [{ARGS.name}], Version: {VERSION}")
logger.info(f"Transport: {ARGS.transport}")
logger.info(f"DB Context clean interval (seconds): {ARGS.close_unused_connections_interval}")

if ARGS.transport != "stdio":
    logger.info(f"Host: {ARGS.host}, Port: {ARGS.port}")

if ARGS.transport == "streamable-http":
    logger.info(f"Expected headers: {list(SUPPORTED_HEADERS.keys())}")

else:
    logger.info(f"Expected environment variables: {SUPPORTED_ENV_VARS}")

if ARGS.debug:
    logger.info(f"Running in debug mode")


@mcp.tool(description=MCPTool.all_table_names.to_description())
def all_table_names(ctx: Context | None = None) -> str:
    logger.info("Retrieving all table names")

    request_context = RequestContext.load(ctx)

    all_tables = request_context.db_context.get_tables()

    logger.info(f"{len(all_tables):,.0f} table available")

    result = ", ".join(all_tables)

    return result

@mcp.tool(description=MCPTool.filter_table_names.to_description())
def filter_table_names(q: str, ctx: Context | None = None) -> str:
    request_context = RequestContext.load(ctx)

    query = request_context.get_parameter("q", q)

    logger.info(f"Retrieving all table names containing '{query}'")

    filtered_tables = request_context.db_context.get_tables(query)

    logger.info(f"{len(filtered_tables):,.0f} table names containing '{query}'")

    result = ", ".join(filtered_tables)

    return result


@mcp.tool(description=MCPTool.schema_definitions.to_description())
async def schema_definitions(table_names: list[str], ctx: Context | None = None) -> str:
    request_context = RequestContext.load(ctx)

    response_parser = ResponseFormatter(request_context)

    result = response_parser.get_schema_list_response(table_names)

    return result

@mcp.tool(description=MCPTool.execute_query.to_description())
async def execute_query(query: str, params, ctx: Context | None = None) -> str:
    request_context = RequestContext.load(ctx)

    response_parser = ResponseFormatter(request_context)

    result = response_parser.get_execute_query_response(query, params)

    return result


def main():
    stop_event = threading.Event()
    
    thread = threading.Thread(target=RequestContext.dispose_unused_connections, args=(stop_event,), daemon=True)
            
    try:
        thread.start()
        
        mcp.run(transport=ARGS.transport)
            
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
    
    finally:    
        stop_event.set()
        thread.join()
    

if IS_ENTRYPOINT:
    main()
