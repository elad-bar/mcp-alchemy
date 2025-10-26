# Vertica MCP Server Dockerfile - Multi-Tenant Version
# No environment variables needed - clients provide connection details at runtime
FROM python:3.11-slim
 
# Set working directory
WORKDIR /app
 
# Ensure Python can import the copied package directory
ENV PYTHONPATH=/app
 
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
 
# Copy requirements
COPY requirements.txt .
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
COPY ./mcp_alchemy/ ./mcp_alchemy/
 
# Create a non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser
 
# Expose port for HTTP transport
EXPOSE 8000
 
# Run the server as a module so package imports resolve
CMD ["python", "mcp_alchemy/server.py", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]