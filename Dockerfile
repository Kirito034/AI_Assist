# Use a minimal Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for PyQt5, OpenGL, and Xvfb
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libegl1-mesa \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable to use the virtual display
ENV DISPLAY=:99

# Copy project files (excluding .env)
COPY . /app

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r Requirements.txt && \
    pip install --no-cache-dir PyQt5 PyQt5-sip

# Expose Railway's dynamic port
EXPOSE 5000

# Ensure Railway's dynamic port is used
ENV PORT=5000

# Command to run the application with Xvfb
CMD ["bash", "-c", "Xvfb :99 -screen 0 1024x768x16 & python3 /app/app.py"]
