# Aras MCP Streamable HTTP Server - Docker Image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY streamable_server.py .
COPY streamable_client.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash aras && \
    chown -R aras:aras /app
USER aras

# Expose the default port
EXPOSE 8123

# Default command - can be overridden
CMD ["python", "streamable_server.py", "--host", "0.0.0.0", "--port", "8123"]
