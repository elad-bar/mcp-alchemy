# Vertica MCP Server Dockerfile - Multi-Tenant Version
# Connection details via env defaults and/or HTTP headers at runtime
FROM python:3.11-slim
 
# Set working directory
WORKDIR /app
 
# Ensure Python can import the copied package directory
ENV PYTHONPATH=/app

# Build argument to enable debug mode
ARG DEBUG_MODE=false
ENV DEBUG_MODE=${DEBUG_MODE}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
 
# Copy requirements
COPY requirements.txt .
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
COPY ./mcp_alchemy/ ./mcp_alchemy/
COPY entrypoint.sh .
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Expose port for HTTP transport
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]