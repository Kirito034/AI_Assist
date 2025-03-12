# Use Python 3.9 slim version
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files to container
COPY . /app

# Ensure Python is upgraded
RUN python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r Requirements.txt

# Expose the necessary port
EXPOSE 80

# Run the application
CMD ["python3", "/app/app.py"]
