# FastMCP Marker - Docker Configuration
# Gebruikt NVIDIA CUDA base image voor GPU ondersteuning

FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Metadata
LABEL maintainer="FastMCP Marker Team"
LABEL description="PDF-to-Markdown conversion service with CUDA support"
LABEL version="0.1.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TORCH_DEVICE=cuda
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=host.docker.internal:11434

# Install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA for Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update

# Install Python 3.12
RUN apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.12 /usr/bin/python

# Install uv package manager (nieuwere methode)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Verify uv installation
RUN uv --version

# Set working directory
WORKDIR /app

# Copy project files voor betere Docker layer caching
COPY pyproject.toml uv.lock ./
COPY stubs/ ./stubs/

# Install Python dependencies with uv (met optimale configuratie)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/start_services.sh

# Create necessary directories
RUN mkdir -p /app/data /app/output /app/logs

# Expose ports
EXPOSE 8000 7860

# Health check - check both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || curl -f http://localhost:7860/ || exit 1

# Default command - start both services
CMD ["/app/start_services.sh"]
