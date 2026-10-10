FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Hugging Face Spaces uses 7860 by default)
EXPOSE 7860
ENV PORT=7860
ENV HOST=0.0.0.0

# Start the application
CMD ["python", "run_server.py"]
