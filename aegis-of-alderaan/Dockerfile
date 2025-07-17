# Aegis of Alderaan - Multi-Service Container
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files first for better caching
COPY guardian-server/requirements.txt /app/guardian-requirements.txt
COPY agent/requirements.txt /app/agent-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r guardian-requirements.txt
RUN pip install --no-cache-dir -r agent-requirements.txt
RUN pip install --no-cache-dir psutil asyncio-mqtt google-generativeai

# Copy application files
COPY guardian-server/ /app/guardian-server/
COPY agent/ /app/agent/
COPY .env /app/.env

# Copy deployment scripts
COPY *.py /app/

# Create logs directory
RUN mkdir -p /app/logs

# Expose Guardian port
EXPOSE 3001

# Environment variables for cloud deployment
ENV PORT=3001
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check for Guardian
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Default command runs Guardian server
# Can be overridden for agent deployment
CMD ["python", "guardian-server/app.py"]

# Alternative agent command (used by render.yaml):
# CMD ["python", "agent/main.py"]
