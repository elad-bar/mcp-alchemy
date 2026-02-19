#!/bin/sh
set -e

if [ -n "$DB_DIALECT_PACKAGES" ]; then
    IFS=','
    for package in $DB_DIALECT_PACKAGES; do
        package=$(echo "$package" | xargs)
        if [ -n "$package" ]; then
            echo "Installing dialect package: $package"
            pip install --quiet "$package"
            echo "Successfully installed: $package"
        fi
    done
    unset IFS
fi

if [ "$DEBUG_MODE" = "true" ]; then
    exec python mcp_alchemy/server.py --transport streamable-http --host 0.0.0.0 --port 8000 --debug true
else
    exec python mcp_alchemy/server.py --transport streamable-http --host 0.0.0.0 --port 8000
fi
