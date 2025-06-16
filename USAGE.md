# MCP Server with SQL Alchemy and Vertica Support

This project provides a server implementation for running SQL Alchemy with Vertica database support through the MCP (Model-Controller-Provider) framework. It enables efficient analytics operations using Cursor IDE.

## Running the MCP Server

Create a `mcp.json` file in your project .cursor directory. Here's a working example:

```json
{
    "mcpServers": {
        "mcp-alchemy": {
            "command": "uvx",
            "args": [
                "--from", "https://test-files.pythonhosted.org/packages/86/86/7d01520ef628edc0a8407353dad7b6b04fe3b3edec565a6468d6119db66b/mcp_alchemy_with_vertica-2025.6.11.102851-py3-none-any.whl",
                "--with", "vertica_python",
                "mcp-alchemy", "--no-cache"
            ],
            "env": {
                "DB_URL": "vertica+vertica_python://username:password@host:port/dbname"
            }
        }
    }
}
```

#### Configuration Parameters Explained

The `mcp.json` configuration has the following structure:

1. `mcpServers`: Top-level object containing server configurations
   - `mcp-alchemy`: Server configuration name
     - `command`: The command to run (`uvx`)
     - `args`: Array of command-line arguments
       - `--from`: Path to the local package wheel file (format: `mcp_alchemy_with_vertica-{version}-py3-none-any.whl`)
       - `--with`: Additional dependencies to install
       - `mcp-alchemy`: The package to run
       - `--no-cache`: Disable caching
     - `env`: Environment variables
       - `DB_URL`: Database connection URL in the format: `vertica+vertica_python://username:password@host:port/dbname`

## Usage in Cursor IDE

1. Start the MCP server using either method above
2. In Cursor IDE:
   - Open your project
   - The MCP server will automatically connect using your chosen configuration method
   - You can now use SQL Alchemy models and queries with Vertica support

## Troubleshooting

1. Connection Issues:
   - Verify Vertica server is running and accessible
   - Check network connectivity
   - Validate credentials in your chosen configuration method
   - Ensure the package wheel file path is correct in mcp.json
   - Verify the DB_URL format in mcp.json

2. Performance Issues:
   - Adjust pool_size and max_overflow in configuration
   - Monitor connection usage
   - Check Vertica server resources

## Security Considerations

- Never commit `mcp.json` with real credentials to version control
- Use environment variables for sensitive information
- Implement proper access controls in Vertica
- Regularly rotate database credentials
- Keep the package wheel file in a secure location

## Support

For issues and feature requests, please contact the development team or create an issue in the project repository.

## License

[Specify your license here] 
