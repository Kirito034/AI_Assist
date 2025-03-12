# Use Python 3.9 slim version
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PyQt5
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    libxkbcommon-x11-0 \
    libegl1-mesa \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files to container
COPY . /app

# Ensure Python is upgraded
RUN python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r Requirements.txt

# Install PyQt5 separately to ensure compatibility
RUN pip install PyQt5 PyQt5-sip

# Expose the necessary port
EXPOSE 80

# Run the application
CMD ["python3", "/app/app.py"]
