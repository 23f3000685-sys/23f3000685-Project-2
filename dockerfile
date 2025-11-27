FROM mcr.microsoft.com/playwright/python:v1.49.0-focal

# Create app directory
WORKDIR /app

# Copy code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
