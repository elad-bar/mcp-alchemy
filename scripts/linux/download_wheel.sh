#!/bin/bash

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script requires root privileges. Please run with sudo."
        exit 1
    fi
}

# Function to check path for spaces and handle it
handle_path_with_spaces() {
    local path="$1"
    
    if [[ "$path" =~ [[:space:]] ]]; then
        echo "Warning: The current path contains spaces which may cause issues with Cursor IDE."
        echo "Please provide an alternative path without spaces:"
        read -r new_path
        
        # Validate the new path
        while [[ "$new_path" =~ [[:space:]] ]]; do
            echo "Error: The provided path still contains spaces. Please provide a path without spaces:"
            read -r new_path
        done
        
        # Create directory if it doesn't exist
        mkdir -p "$new_path"
        
        echo "$new_path"
        return
    fi
    
    echo "$path"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ -f /etc/debian_version ]]; then
        echo "debian"
    elif [[ -f /etc/redhat-release ]]; then
        echo "redhat"
    else
        echo "unknown"
    fi
}

# Function to check and install Python 3.12
install_python312() {
    echo "Checking Python installation..."
    if ! command -v python3.12 &> /dev/null; then
        echo "Python 3.12 not found. Installing..."
        
        case $(detect_os) in
            "macos")
                if ! command -v brew &> /dev/null; then
                    echo "Error: Homebrew is required but not installed"
                    exit 1
                fi
                if ! brew install python@3.12; then
                    echo "Error: Failed to install Python 3.12 via Homebrew"
                    exit 1
                fi
                ;;
            "debian")
                if ! apt-get update; then
                    echo "Error: Failed to update package lists"
                    exit 1
                fi
                if ! apt-get install -y software-properties-common; then
                    echo "Error: Failed to install software-properties-common"
                    exit 1
                fi
                if ! add-apt-repository -y ppa:deadsnakes/ppa; then
                    echo "Error: Failed to add deadsnakes PPA"
                    exit 1
                fi
                if ! apt-get update; then
                    echo "Error: Failed to update package lists after adding PPA"
                    exit 1
                fi
                if ! apt-get install -y python3.12; then
                    echo "Error: Failed to install Python 3.12"
                    exit 1
                fi
                ;;
            "redhat")
                if ! dnf install -y python3.12; then
                    echo "Error: Failed to install Python 3.12"
                    exit 1
                fi
                ;;
            *)
                echo "Unsupported OS for automatic Python installation"
                exit 1
                ;;
        esac
        
        # Verify installation
        if ! command -v python3.12 &> /dev/null; then
            echo "Error: Python 3.12 installation verification failed"
            exit 1
        fi
    fi
}

# Function to check and install UVX
install_uvx() {
    echo "Checking UVX installation..."
    if ! command -v uvx &> /dev/null; then
        echo "UVX not found. Installing..."
        
        case $(detect_os) in
            "macos")
                if ! command -v brew &> /dev/null; then
                    echo "Error: Homebrew is required but not installed"
                    exit 1
                fi
                if ! brew install astral; then
                    echo "Error: Failed to install UVX via Homebrew"
                    exit 1
                fi
                ;;
            "debian"|"redhat")
                if ! curl -sSf https://astral.sh/uv/install.sh | sh; then
                    echo "Error: Failed to install UVX"
                    exit 1
                fi
                ;;
            *)
                echo "Unsupported OS for automatic UVX installation"
                exit 1
                ;;
        esac
        
        # Verify installation
        if ! command -v uvx &> /dev/null; then
            echo "Error: UVX installation verification failed"
            exit 1
        fi
    fi
}

# Main script execution
check_root

# Install dependencies
install_python312
install_uvx

# Check current path for spaces
CURRENT_PATH=$(pwd)
TARGET_PATH=$(handle_path_with_spaces "$CURRENT_PATH")

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

# Download the wheel file to the target path
WHEEL_PATH="$TARGET_PATH/$WHEEL_FILE"
echo "Downloading $WHEEL_FILE to $TARGET_PATH..."
curl -L "$WHEEL_URL" -o "$WHEEL_PATH"

if [ $? -eq 0 ]; then
    echo "Successfully downloaded: $WHEEL_PATH"
    # Make the file executable
    chmod +x "$WHEEL_PATH"
    
    # Print recommended mcp.json
    echo -e "\nRecommended mcp.json configuration:"
    cat << EOF
{
    "mcpServers": {
        "mcp-alchemy": {
            "command": "uvx",
            "args": [
                "--from", "$WHEEL_PATH",
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