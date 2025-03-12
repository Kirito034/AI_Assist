# Use a Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for PyQt5 and OpenGL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libegl1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Copy .env file
COPY .env /app/.env

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install required Python packages
RUN pip install --no-cache-dir -r Requirements.txt

# Install PyQt5 separately
RUN pip install PyQt5 PyQt5-sip

# Expose the necessary port
EXPOSE 80

# Command to run the application
CMD ["python3", "/app/app.py"]
