# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:12.6.2-runtime-ubuntu24.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .
COPY main.py .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the agent via FastAPI wrapper
CMD ["python3", "main.py"]
