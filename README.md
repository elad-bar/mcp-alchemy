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

For streamable-http transport, use the MCP HTTP client. Configuration is merged from **container environment** and **HTTP headers** (header wins when both are set):

| Header | Environment variable | Description |
|--------|----------------------|-------------|
| `X-DB-URL` | `DB_URL` | Full SQLAlchemy URL (optional if parts below are complete) |
| `X-DB-DRIVER` | `DB_DRIVER` | Driver/dialect, e.g. `postgresql+psycopg2` |
| `X-DB-HOST` | `DB_HOST` | Database host |
| `X-DB-PORT` | `DB_PORT` | Database port (optional) |
| `X-DB-NAME` | `DB_NAME` | Database name |
| `X-DB-USER` | `DB_USER` | Username |
| `X-DB-PASSWORD` | `DB_PASSWORD` | Password |
| `X-DB-ENGINE-OPTIONS` | `DB_ENGINE_OPTIONS` | JSON string with SQLAlchemy engine options (optional) |
| `X-EXECUTE-QUERY-MAX-CHARS` | `EXECUTE_QUERY_MAX_CHARS` | Maximum output length (optional) |

None of the connection fields are required in the environment; you can supply everything per client via headers, or set shared defaults in the container and override per tenant in headers (typical for multi-instance Docker deployments).

**Full URL (unchanged):**

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

**Shared server env + per-client credentials and database:**

Container:

```bash
docker run -p 8000:8000 \
  -e DB_DIALECT_PACKAGES=psycopg2-binary \
  -e DB_DRIVER=postgresql+psycopg2 \
  -e DB_HOST=db.internal \
  -e DB_PORT=5432 \
  mcp-alchemy
```

Client (only tenant-specific headers):

```json
{
  "mcpServers": {
    "tenant_a": {
      "url": "http://localhost:8000/mcp",
      "env": {
        "X-DB-NAME": "tenant_a_db",
        "X-DB-USER": "tenant_a_user",
        "X-DB-PASSWORD": "secret"
      }
    }
  }
}
```

### Docker Deployment

A `Dockerfile` and `entrypoint.sh` are included in the repository. The entrypoint script supports installing SQLAlchemy dialect packages at container startup via the `DB_DIALECT_PACKAGES` environment variable.

**Build the image:**
```bash
docker build -t mcp-alchemy .
```

**Run with connection parts in env (credentials can also come from client headers):**
```bash
docker run -p 8000:8000 \
  -e DB_DIALECT_PACKAGES=sqlalchemy-vertica-python \
  -e DB_DRIVER=vertica+vertica_python \
  -e DB_HOST=host \
  -e DB_PORT=5433 \
  -e DB_NAME=dbname \
  -e DB_USER=user \
  -e DB_PASSWORD=password \
  mcp-alchemy
```

**Run with full URL (legacy):**
```bash
docker run -p 8000:8000 \
  -e DB_DIALECT_PACKAGES=sqlalchemy-vertica-python \
  -e DB_URL="vertica+vertica_python://user:password@host:5433/dbname" \
  mcp-alchemy
```

**Run with multiple dialect packages:**
```bash
docker run -p 8000:8000 \
  -e DB_DIALECT_PACKAGES=psycopg2-binary,pymysql \
  -e DB_URL="postgresql://user:password@host/dbname" \
  mcp-alchemy
```

**Run with debug mode enabled:**
```bash
docker run -p 8000:8000 \
  -e DB_DIALECT_PACKAGES=psycopg2-binary \
  -e DEBUG_MODE=true \
  mcp-alchemy
```

The server starts on port 8000 with streamable-http transport by default.

### Security Considerations

When running as a remote server:

- **Network Security**: Use firewalls and VPNs to restrict access
- **Authentication**: Consider implementing authentication layers
- **Database Permissions**: Use database users with minimal required permissions
- **TLS/SSL**: Use encrypted connections for database and MCP communication
- **Environment Variables**: Secure sensitive configuration like database credentials; prefer TLS in front of the MCP HTTP port when sending passwords in headers

## Environment Variables

Connection settings apply to **stdio** from the environment only. For **streamable-http**, the same variables are optional defaults merged with `X-DB-*` headers (header overrides env).

- `DB_URL`: Full SQLAlchemy [database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) (optional if driver, host, name, user, and password are provided)
- `DB_DRIVER`: SQLAlchemy driver/dialect (e.g. `postgresql+psycopg2`, `vertica+vertica_python`)
- `DB_HOST`: Database host
- `DB_PORT`: Database port (optional)
- `DB_NAME`: Database name
- `DB_USER`: Database user (optional in env if sent via headers)
- `DB_PASSWORD`: Database password (optional in env if sent via headers)
- `EXECUTE_QUERY_MAX_CHARS`: Maximum output length (optional, default 4000)
- `DB_ENGINE_OPTIONS`: JSON string containing additional SQLAlchemy engine options (optional)
- `DB_DIALECT_PACKAGES`: Comma-separated list of pip packages to install at startup (Docker only, optional). Example: `sqlalchemy-vertica-python,pymysql`

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
