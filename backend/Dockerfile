FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including unzip for Deno
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Deno for yt-dlp JS challenge solving
RUN curl -fsSL https://deno.land/install.sh | sh && \
    echo 'export DENO_INSTALL="/root/.deno"' >> ~/.bashrc && \
    echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> ~/.bashrc

# Add Deno to PATH for this build
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directory
RUN mkdir -p /app/temp

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
