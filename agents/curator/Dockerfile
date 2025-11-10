FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY *.py ./

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run with uvicorn
CMD exec python main.py
