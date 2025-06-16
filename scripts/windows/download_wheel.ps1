# Function to check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check path for spaces and handle it
function Handle-PathWithSpaces {
    param (
        [string]$Path
    )
    
    if ($Path -match '\s') {
        Write-Host "Warning: The current path contains spaces which may cause issues with Cursor IDE."
        Write-Host "Please provide an alternative path without spaces:"
        $newPath = Read-Host "Enter new path"
        
        # Validate the new path
        while ($newPath -match '\s') {
            Write-Host "Error: The provided path still contains spaces. Please provide a path without spaces:"
            $newPath = Read-Host "Enter new path"
        }
        
        # Create directory if it doesn't exist
        if (-not (Test-Path $newPath)) {
            New-Item -ItemType Directory -Path $newPath -Force | Out-Null
        }
        
        return $newPath
    }
    
    return $Path
}

# Function to check and install Python 3.12
function Install-Python312 {
    Write-Host "Checking Python installation..."
    $pythonVersion = python --version 2>&1
    if (-not ($pythonVersion -match "Python 3.12")) {
        Write-Host "Python 3.12 not found. Installing..."
        
        # Download Python 3.12 installer
        $pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        $installerPath = "$env:TEMP\python-3.12.0-amd64.exe"
        
        try {
            Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
        }
        catch {
            Write-Host "Error: Failed to download Python installer: $_"
            exit 1
        }
        
        # Install Python with required options
        try {
            $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait -PassThru
            if ($process.ExitCode -ne 0) {
                Write-Host "Error: Python installation failed with exit code $($process.ExitCode)"
                exit 1
            }
        }
        catch {
            Write-Host "Error: Failed to install Python: $_"
            exit 1
        }
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Verify installation
        $pythonVersion = python --version 2>&1
        if (-not ($pythonVersion -match "Python 3.12")) {
            Write-Host "Error: Python 3.12 installation verification failed"
            exit 1
        }
    }
}

# Function to check and install UVX
function Install-UVX {
    Write-Host "Checking UVX installation..."
    $uvxVersion = uvx --version 2>&1
    if (-not $uvxVersion) {
        Write-Host "UVX not found. Installing..."
        
        # Download Astral installer
        $astralUrl = "https://astral.sh/uv/latest/windows/uv-installer.exe"
        $installerPath = "$env:TEMP\uv-installer.exe"
        
        try {
            Invoke-WebRequest -Uri $astralUrl -OutFile $installerPath
        }
        catch {
            Write-Host "Error: Failed to download UVX installer: $_"
            exit 1
        }
        
        # Install UVX
        try {
            $process = Start-Process -FilePath $installerPath -ArgumentList "--install" -Wait -PassThru
            if ($process.ExitCode -ne 0) {
                Write-Host "Error: UVX installation failed with exit code $($process.ExitCode)"
                exit 1
            }
        }
        catch {
            Write-Host "Error: Failed to install UVX: $_"
            exit 1
        }
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Verify installation
        $uvxVersion = uvx --version 2>&1
        if (-not $uvxVersion) {
            Write-Host "Error: UVX installation verification failed"
            exit 1
        }
    }
}

# Main script execution
if (-not (Test-Administrator)) {
    Write-Host "This script requires administrator privileges. Please run as administrator."
    exit 1
}

# Install dependencies
Install-Python312
Install-UVX

# Check current path for spaces
$CurrentPath = (Get-Location).Path
$TargetPath = Handle-PathWithSpaces -Path $CurrentPath

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

    # Download the wheel file to the target path
    $WheelPath = Join-Path $TargetPath $WHEEL_FILE
    Write-Host "Downloading $WHEEL_FILE to $TargetPath..."
    Invoke-WebRequest -Uri $WHEEL_URL -OutFile $WheelPath
    Write-Host "Successfully downloaded: $WheelPath"
    
    # Print recommended mcp.json
    Write-Host "`nRecommended mcp.json configuration:"
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