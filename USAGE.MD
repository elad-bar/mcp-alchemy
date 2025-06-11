# MCP Server with SQL Alchemy and Vertica Support

This project provides a server implementation for running SQL Alchemy with Vertica database support through the MCP (Model-Controller-Provider) framework. It enables efficient analytics operations using Cursor IDE.

## Package Download

The package is hosted on test.pypi.org. You can download the wheel file for a specific version using the scripts below.

### For Mac / Linux

Save this script as `download_wheel.sh`:

```bash
#!/bin/bash

# Get all versions from simple API
SIMPLE_URL="https://test.pypi.org/simple/mcp-alchemy-with-vertica/"
echo "Fetching available versions from: $SIMPLE_URL"

# Download and process the content
SIMPLE_CONTENT=$(curl -s "$SIMPLE_URL")
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch content from $SIMPLE_URL"
    exit 1
fi

# Extract version numbers and URLs using grep and sed
# Format: version|url
VERSIONS_AND_URLS=$(echo "$SIMPLE_CONTENT" | \
    grep -o 'href="[^"]*mcp_alchemy_with_vertica-[0-9.]\+-py3-none-any\.whl[^"]*"' | \
    sed -E 's/href="([^"]*mcp_alchemy_with_vertica-([0-9.]+)-py3-none-any\.whl[^"]*)"/\2|\1/g')

if [ -z "$VERSIONS_AND_URLS" ]; then
    echo "Error: No versions found"
    exit 1
fi

# Sort versions and get the latest one
# Using sort -V for version number sorting
LATEST=$(echo "$VERSIONS_AND_URLS" | sort -t'|' -k1,1Vr | head -n1)
VERSION=$(echo "$LATEST" | cut -d'|' -f1)
WHEEL_URL=$(echo "$LATEST" | cut -d'|' -f2)

echo "Latest version found: $VERSION"

WHEEL_FILE="mcp_alchemy_with_vertica-$VERSION-py3-none-any.whl"
echo "Found wheel URL: $WHEEL_URL"

# Download the wheel file
echo "Downloading $WHEEL_FILE..."
curl -L "$WHEEL_URL" -o "$WHEEL_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully downloaded: $WHEEL_FILE"
    # Make the file executable
    chmod +x "$WHEEL_FILE"
    
    # Print recommended mcp.json
    echo -e "\nRecommended mcp.json configuration:"
    cat << EOF
{
    "mcpServers": {
        "mcp-alchemy": {
            "command": "uvx",
            "args": [
                "--from", "$(pwd)/$WHEEL_FILE",
                "--with", "vertica_python",
                "mcp-alchemy", "--no-cache"
            ],
            "env": {
                "DB_URL": "vertica+vertica_python://username:password@host:port/dbname"
            }
        }
    }
}
EOF
else
    echo "Error: Failed to download the wheel file"
    exit 1
fi
```

Make it executable and run:
```bash
chmod +x download_wheel.sh
./download_wheel.sh
```

### For Windows

Save this script as `download_wheel.ps1`:

```powershell
# Get all versions from simple API
$SIMPLE_URL = "https://test.pypi.org/simple/mcp-alchemy-with-vertica/"
Write-Host "Fetching available versions from: $SIMPLE_URL"

try {
    # Download and process the content
    $SIMPLE_CONTENT = Invoke-WebRequest -Uri $SIMPLE_URL -UseBasicParsing

    # Extract version numbers and URLs using regex
    $VERSIONS_AND_URLS = $SIMPLE_CONTENT.Content | 
        Select-String -Pattern 'href="([^"]*mcp_alchemy_with_vertica-([0-9.]+)-py3-none-any\.whl[^"]*)"' -AllMatches |
        ForEach-Object { $_.Matches } |
        ForEach-Object {
            $version = $_.Groups[2].Value
            $url = $_.Groups[1].Value
            [PSCustomObject]@{
                Version = $version
                Url = $url
            }
        }

    if (-not $VERSIONS_AND_URLS) {
        Write-Host "Error: No versions found"
        exit 1
    }

    # Sort versions and get the latest one
    # Using PowerShell's Version type for proper version sorting
    $LATEST = $VERSIONS_AND_URLS | 
        Sort-Object { [Version]($_.Version -replace '(\d+)\.(\d+)\.(\d+)\.(\d+)', '$1.$2.$3.$4') } -Descending |
        Select-Object -First 1

    $VERSION = $LATEST.Version
    $WHEEL_URL = $LATEST.Url

    Write-Host "Latest version found: $VERSION"

    $WHEEL_FILE = "mcp_alchemy_with_vertica-$VERSION-py3-none-any.whl"
    Write-Host "Found wheel URL: $WHEEL_URL"

    # Download the wheel file
    Write-Host "Downloading $WHEEL_FILE..."
    Invoke-WebRequest -Uri $WHEEL_URL -OutFile $WHEEL_FILE
    Write-Host "Successfully downloaded: $WHEEL_FILE"
    
    # Print recommended mcp.json
    Write-Host "`nRecommended mcp.json configuration:"
    $CurrentPath = (Get-Location).Path
    $WheelPath = Join-Path $CurrentPath $WHEEL_FILE
    $MCP_JSON = @{
        mcpServers = @{
            "mcp-alchemy" = @{
                command = "uvx"
                args = @(
                    "--from", $WheelPath
                    "--with", "vertica_python"
                    "mcp-alchemy", "--no-cache"
                )
                env = @{
                    DB_URL = "vertica+vertica_python://username:password@host:port/dbname"
                }
            }
        }
    }
    $MCP_JSON | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "Error: $_"
    exit 1
}
```

Run in PowerShell:
```powershell
.\download_wheel.ps1
```

After downloading the wheel file, you can use it in your `mcp.json` configuration or with the `uvx` command.

## Running the MCP Server

There are two ways to run the MCP server:

### 1. Using Command Line (uvx)

Run the server using the `uvx` command:

```bash
VERSION="2025.6.10.101944"
uvx --from PATH_TO_PACKAGE/mcp_alchemy_with_vertica-$VERSION-py3-none-any.whl \
    --with vertica_python \
    mcp-alchemy --no-cache
```

Note: The package wheel filename includes the version number (e.g., `2025.6.10.122832`). Make sure to use the correct version for your setup.

Set the database connection URL as an environment variable:
```bash
export DB_URL="vertica+vertica_python://username:password@host:port/dbname"
```

Command line parameters explained:
- `--from`: Path to the local package wheel file (format: `mcp_alchemy_with_vertica-{version}-py3-none-any.whl`)
- `--with`: Additional dependencies to install (vertica_python)
- `mcp-alchemy`: The package to run
- `--no-cache`: Disable caching

### 2. Using Configuration File (mcp.json)

Create a `mcp.json` file in your project root. Here's a working example:

```json
{
    "mcpServers": {
        "mcp-alchemy": {
            "command": "uvx",
            "args": [
                "--from", "PATH_TO_PACKAGE\\mcp_alchemy_with_vertica-2025.6.10.122832-py3-none-any.whl",
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