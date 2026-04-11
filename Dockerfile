# --------------------------------------------------
# Base Image
# --------------------------------------------------
# Use a lightweight Python image to stay within resource limits
FROM python:3.10-slim

# --------------------------------------------------
# Environment Variables
# --------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# --------------------------------------------------
# Set Working Directory
# --------------------------------------------------
WORKDIR /app

# --------------------------------------------------
# Install System Dependencies
# --------------------------------------------------
# Install minimal dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Copy Dependency Files
# --------------------------------------------------
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# --------------------------------------------------
# Install Python Dependencies
# --------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------
# Copy Project Files
# --------------------------------------------------
COPY . .

# --------------------------------------------------
# Expose Port for Hugging Face Spaces
# --------------------------------------------------
EXPOSE 7860

# --------------------------------------------------
# Health Check (Optional but Recommended)
# --------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# --------------------------------------------------
# Start the FastAPI Application
# --------------------------------------------------
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]