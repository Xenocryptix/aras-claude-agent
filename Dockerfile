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
COPY example_usage.py .
COPY test_streamable.py .
COPY healthcheck.py .

# Copy documentation
COPY README.md .
COPY STREAMABLE_README.md .
COPY LICENSE .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash aras && \
    chown -R aras:aras /app
USER aras

# Expose the default port
EXPOSE 8123

# Health check using Python script
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python healthcheck.py || exit 1

# Default command - can be overridden
CMD ["python", "streamable_server.py", "--host", "0.0.0.0", "--port", "8123"]
