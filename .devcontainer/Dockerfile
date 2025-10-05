# FastMCP Marker - Development Container
# Gebaseerd op de productie Dockerfile maar geoptimaliseerd voor development

FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Metadata
LABEL maintainer="FastMCP Marker Development Team"
LABEL description="Development environment for FastMCP Marker with CUDA support"
LABEL version="0.1.0-dev"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TORCH_DEVICE=cuda
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTHONPATH=/workspace

# Install system dependencies (uitgebreider voor development)
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
    vim \
    nano \
    htop \
    tree \
    jq \
    wget \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA for Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update

# Install Python 3.12
RUN apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3.12-distutils \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.12 /usr/bin/python

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Verify uv installation
RUN uv --version

# Set working directory
WORKDIR /workspace

# Copy project files voor betere Docker layer caching
COPY pyproject.toml uv.lock ./
COPY stubs/ ./stubs/

# Install Python dependencies with uv (inclusief dev dependencies)
RUN uv sync --frozen

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/data /workspace/output /workspace/logs

# Make startup script executable
RUN chmod +x /workspace/start_services.sh

# Expose ports
EXPOSE 8000 7860

# Development-specific setup
RUN echo 'alias ll="ls -la"' >> /root/.bashrc
RUN echo 'alias la="ls -A"' >> /root/.bashrc
RUN echo 'alias l="ls -CF"' >> /root/.bashrc
RUN echo 'export PS1="\[\033[01;32m\]FastMCP-Dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /root/.bashrc

# Health check voor development
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import torch; print('CUDA available:', torch.cuda.is_available())" || exit 1

# Default command voor development (interactive shell)
CMD ["/bin/bash"]
