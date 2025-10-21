import argparse

DEFAULT_MCP_SERVER_NAME = "MCP Alchemy"
DEFAULT_MCP_SERVER_HOST = "127.0.0.1"
DEFAULT_MCP_SERVER_PORT = 8000
DEFAULT_MCP_SERVER_TRANSPORT = "stdio"
DEFAULT_MCP_SERVER_DEBUG = False
DEFAULT_MCP_SERVER_CLOSE_UNUSED_INTERVAL = 600


class MCPServerArguments:
    name: str
    host: str
    port: int
    transport: str
    debug: bool
    close_unused_connections_interval: int

    def __init__(self,
                 name: str = DEFAULT_MCP_SERVER_NAME,
                 host: str = DEFAULT_MCP_SERVER_HOST,
                 port: int = DEFAULT_MCP_SERVER_PORT,
                 transport: str = DEFAULT_MCP_SERVER_TRANSPORT,
                 debug: bool = DEFAULT_MCP_SERVER_DEBUG,
                 close_unused_connections_interval: int = DEFAULT_MCP_SERVER_CLOSE_UNUSED_INTERVAL
        ):

        self.name = name
        self.host = host
        self.port = port
        self.transport = transport
        self.debug = debug
        self.close_unused_connections_interval = close_unused_connections_interval

    @staticmethod
    def load(is_entrypoint: bool):
        if is_entrypoint:
            p = argparse.ArgumentParser(description="Run MCP Alchemy")

            # Name for the MCP Server
            p.add_argument(
                "--name",
                default=DEFAULT_MCP_SERVER_NAME
            )

            # Host for the MCP Server
            # Relevant for SSE / Streamable-HTTP,
            # If not set for those transport layers - will be accessible only from localhost
            p.add_argument(
                "--host",
                default=DEFAULT_MCP_SERVER_HOST
            )

            # Port for the MCP Server, relevant for SSE / Streamable-HTTP
            p.add_argument(
                "--port",
                type=int,
                default=DEFAULT_MCP_SERVER_PORT
            )

            # Which transport layer to use (stdio, sse, streamable-http)
            p.add_argument(
                "--transport",
                default=DEFAULT_MCP_SERVER_TRANSPORT,
                choices=["stdio", "sse", "streamable-http"]
            )

            # Run with debug logs
            p.add_argument(
                "--debug",
                type=bool,
                default=DEFAULT_MCP_SERVER_DEBUG
            )

            # Interval in seconds to check if DB connection is not being used
            p.add_argument(
                "--close-unused-connections-interval",
                type=int,
                default=DEFAULT_MCP_SERVER_CLOSE_UNUSED_INTERVAL
            )

            args = p.parse_args()

            mcp_args = MCPServerArguments(args.name, args.host, args.port, args.transport, args.debug, args.close_unused_connections_interval)

        else:
            mcp_args = MCPServerArguments()

        return mcp_args
