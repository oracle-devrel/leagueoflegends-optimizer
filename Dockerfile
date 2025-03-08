FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
RUN mkdir -p /opt/oracle
WORKDIR /opt/oracle
RUN curl -L https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip -o instantclient-basiclite-linuxx64.zip \
    && unzip instantclient-basiclite-linuxx64.zip \
    && rm instantclient-basiclite-linuxx64.zip \
    && cd /opt/oracle/instantclient* \
    && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

# Set environment variables for Oracle Instant Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient*:$LD_LIBRARY_PATH
ENV PATH=/opt/oracle/instantclient*:$PATH

# Return to app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml setup.py ./
RUN pip install --no-cache-dir -e .

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p logs models/trained

# Expose ports
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["leagueoptimizer"]

# Default command
CMD ["visualizer"] 