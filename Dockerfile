# Use a minimal Python base image
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

# Copy project files (excluding .env)
COPY . /app

# Install Xvfb to simulate a display for PyAutoGUI
RUN apt-get update && apt-get install -y xvfb

# Set environment variable to use the virtual display
ENV DISPLAY=:99

# Upgrade pip and install dependencies in a single step
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r Requirements.txt && \
    pip install --no-cache-dir PyQt5 PyQt5-sip

# Expose Railway's dynamic port (not fixed 80)
EXPOSE 5000

# Ensure Railway's dynamic port is used
ENV PORT=5000

# Command to run the application
CMD ["python3", "/app/app.py"]
