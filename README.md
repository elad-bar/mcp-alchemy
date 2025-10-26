# MCP Alchemy

<a href="https://www.pulsemcp.com/servers/runekaagaard-alchemy"><img src="https://www.pulsemcp.com/badge/top-pick/runekaagaard-alchemy" width="400" alt="PulseMCP Badge"></a>

**Status: Works great and is in daily use without any known bugs.**

**Status2: I just added the package to PyPI and updated the usage instructions. Please report any issues :)**

Let Claude be your database expert! MCP Alchemy connects Claude Desktop directly to your databases, allowing it to:

- Help you explore and understand your database structure
- Assist in writing and validating SQL queries
- Displays relationships between tables
- Analyze large datasets and create reports

Works with PostgreSQL, MySQL, MariaDB, SQLite, Oracle, MS SQL Server, CrateDB, Vertica,
and a host of other [SQLAlchemy-compatible](https://docs.sqlalchemy.org/en/20/dialects/) databases.

![MCP Alchemy in action](https://raw.githubusercontent.com/runekaagaard/mcp-alchemy/refs/heads/main/screenshot.png)

## Installation

Ensure you have uv installed:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`. You need to add the appropriate database driver in the ``--with`` parameter.

_Note: After a new version release there might be a period of up to 600 seconds while the cache clears locally 
cached causing uv to raise a versioning error. Restarting the MCP client once again solves the error._

### SQLite (built into Python)
```json
{
  "mcpServers": {
    "my_sqlite_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "sqlite:////absolute/path/to/database.db"
      }
    }
  }
}
```

### PostgreSQL
```json
{
  "mcpServers": {
    "my_postgres_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "psycopg2-binary",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "postgresql://user:password@localhost/dbname"
      }
    }
  }
}
```

### MySQL/MariaDB
```json
{
  "mcpServers": {
    "my_mysql_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "pymysql",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "mysql+pymysql://user:password@localhost/dbname"
      }
    }
  }
}
```

### Microsoft SQL Server
```json
{
  "mcpServers": {
    "my_mssql_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "pymssql",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "mssql+pymssql://user:password@localhost/dbname"
      }
    }
  }
}
```

### Oracle
```json
{
  "mcpServers": {
    "my_oracle_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "oracledb",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "oracle+oracledb://user:password@localhost/dbname"
      }
    }
  }
}
```

### CrateDB
```json
{
  "mcpServers": {
    "my_cratedb": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "sqlalchemy-cratedb>=0.42.0.dev1",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "crate://user:password@localhost:4200/?schema=testdrive"
      }
    }
  }
}
```
For connecting to CrateDB Cloud, use a URL like
`crate://user:password@example.aks1.westeurope.azure.cratedb.net:4200?ssl=true`.

### Vertica
```json
{
  "mcpServers": {
    "my_vertica_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.8.15.91819", "--with", "vertica-python",
               "--refresh-package", "mcp-alchemy", "mcp-alchemy"],
      "env": {
        "DB_URL": "vertica+vertica_python://user:password@localhost:5433/dbname",
        "DB_ENGINE_OPTIONS": "{\"connect_args\": {\"ssl\": false}}"
      }
    }
  }
}
```

## Usage as Remote MCP Server

You can also run MCP Alchemy as a standalone remote server that can be accessed by multiple MCP clients. This is useful for:

- Sharing database access across multiple Claude Desktop instances
- Running the server on a different machine
- Integrating with other MCP-compatible tools
- Setting up centralized database access for teams

### Starting the Remote Server

1. **Install the package:**
   ```bash
   pip install mcp-alchemy
   ```

2. **Start the server with SSE / Streamable HTTP transport:**
   ```bash
   python -m mcp_alchemy.server --transport sse --host 0.0.0.0 --port 8000
   ```

   Or with streamable-http transport:
   ```bash
   python -m mcp_alchemy.server --transport streamable-http --host 0.0.0.0 --port 8000
   ```

   The server will be accessible at `http://localhost:8000` (or your specified host/port).

### Connecting from Claude Desktop

#### Using SSE Transport

For SSE transport, configure Claude Desktop to connect via HTTP:

```json
{
  "mcpServers": {
    "remote_alchemy_sse": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "DB_URL": "postgresql://user:password@localhost/dbname"
      }
    }
  }
}
```

#### Using Streamable-HTTP Transport

For streamable-http transport, use the MCP HTTP client:

```json
{
  "mcpServers": {
    "remote_alchemy_http": {
      "url": "http://localhost:8000/mcp",
      "env": {
        "X-DB-URL": "postgresql://user:password@localhost/dbname"
      }
    }
  }
}
```

**Note:** With streamable-http, configuration is passed via HTTP headers:
- `X-DB-URL`: Database connection string
- `X-DB-ENGINE-OPTIONS`: JSON string with SQLAlchemy engine options (optional)
- `X-EXECUTE-QUERY-MAX-CHARS`: Maximum output length (optional)

### Docker Deployment

For production deployments, you can run MCP Alchemy in Docker:

```dockerfile
FROM python:3.11-slim

RUN pip install mcp-alchemy psycopg2-binary

ENV DB_URL="postgresql://user:password@dbhost/dbname"

# Expose port for remote connections
EXPOSE 8000

# Start with SSE transport for remote access
CMD ["python", "-m", "mcp_alchemy.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t mcp-alchemy .
docker run -p 8000:8000 -e DB_URL="postgresql://user:password@host/db" mcp-alchemy
```

**Alternative with streamable-http:**
```dockerfile
CMD ["python", "-m", "mcp_alchemy.server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations

When running as a remote server:

- **Network Security**: Use firewalls and VPNs to restrict access
- **Authentication**: Consider implementing authentication layers
- **Database Permissions**: Use database users with minimal required permissions
- **TLS/SSL**: Use encrypted connections for database and MCP communication
- **Environment Variables**: Secure sensitive configuration like database credentials

## Environment Variables

- `DB_URL`: SQLAlchemy [database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) (required)
- `EXECUTE_QUERY_MAX_CHARS`: Maximum output length (optional, default 4000)
- `DB_ENGINE_OPTIONS`: JSON string containing additional SQLAlchemy engine options (optional)

## Connection Pooling

MCP Alchemy uses connection pooling optimized for long-running MCP servers. The default settings are:

- `pool_pre_ping=True`: Tests connections before use to handle database timeouts and network issues
- `pool_size=1`: Maintains 1 persistent connection (MCP servers typically handle one request at a time)
- `max_overflow=2`: Allows up to 2 additional connections for burst capacity
- `pool_recycle=3600`: Refreshes connections older than 1 hour (prevents timeout issues)
- `isolation_level='AUTOCOMMIT'`: Ensures each query commits automatically

These defaults work well for most databases, but you can override them via `DB_ENGINE_OPTIONS`:

```json
{
  "DB_ENGINE_OPTIONS": "{\"pool_size\": 5, \"max_overflow\": 10, \"pool_recycle\": 1800}"
}
```

For databases with aggressive timeout settings (like MySQL's 8-hour default), the combination of `pool_pre_ping` and `pool_recycle` ensures reliable connections.

## API

### Tools

- **all_table_names**
  - Return all table names in the database
  - No input required
  - Returns comma-separated list of tables
  ```
  users, orders, products, categories
  ```

- **filter_table_names**
  - Find tables matching a substring
  - Input: `q` (string)
  - Returns matching table names
  ```
  Input: "user"
  Returns: "users, user_roles, user_permissions"
  ```

- **schema_definitions**
  - Get detailed schema for specified tables
  - Input: `table_names` (string[])
  - Returns table definitions including:
    - Column names and types
    - Primary keys
    - Foreign key relationships
    - Nullable flags
  ```
  users:
      id: INTEGER, primary key, autoincrement
      email: VARCHAR(255), nullable
      created_at: DATETIME
      
      Relationships:
        id -> orders.user_id
  ```

- **execute_query**
  - Execute SQL query with vertical output format
  - Inputs:
    - `query` (string): SQL query
    - `params` (object, optional): Query parameters
  - Returns results in clean vertical format:
  ```
  1. row
  id: 123
  name: John Doe
  created_at: 2024-03-15T14:30:00
  email: NULL

  Result: 1 rows
  ```
  - Features:
    - Smart truncation of large results
    - Clean NULL value display
    - ISO formatted dates
    - Clear row separation

## Developing

First clone the github repository, install the dependencies and your database driver(s) of choice:

```
git clone git@github.com:runekaagaard/mcp-alchemy.git
cd mcp-alchemy
uv sync
uv pip install psycopg2-binary
```

Then set this in claude_desktop_config.json:

```
...
"command": "uv",
"args": ["run", "--directory", "/path/to/mcp-alchemy", "-m", "mcp_alchemy.server", "main"],
...
```

## My Other LLM Projects

- **[MCP Redmine](https://github.com/runekaagaard/mcp-redmine)** - Let Claude Desktop manage your Redmine projects and issues.
- **[MCP Notmuch Sendmail](https://github.com/runekaagaard/mcp-notmuch-sendmail)** - Email assistant for Claude Desktop using notmuch.
- **[Diffpilot](https://github.com/runekaagaard/diffpilot)** - Multi-column git diff viewer with file grouping and tagging.

## MCP Directory Listings

MCP Alchemy is listed in the following MCP directory sites and repositories:

- [PulseMCP](https://www.pulsemcp.com/servers/runekaagaard-alchemy)
- [Glama](https://glama.ai/mcp/servers/@runekaagaard/mcp-alchemy)
- [MCP.so](https://mcp.so/server/mcp-alchemy)
- [MCP Archive](https://mcp-archive.com/server/mcp-alchemy)
- [Playbooks MCP](https://playbooks.com/mcp/runekaagaard-alchemy)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

## Contributing

Contributions are warmly welcomed! Whether it's bug reports, feature requests, documentation improvements, or code contributions - all input is valuable. Feel free to:

- Open an issue to report bugs or suggest features
- Submit pull requests with improvements
- Enhance documentation or share your usage examples
- Ask questions and share your experiences

The goal is to make database interaction with Claude even better, and your insights and contributions help achieve that.

## License

Mozilla Public License Version 2.0
