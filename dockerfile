# Use an official Python image
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y curl wget gnupg \
    && apt-get install -y libnss3 libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0 libdrm2 libgbm1 libasound2 libxcomposite1 libxrandr2 libxdamage1 libpango-1.0-0 libcairo2 fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy app files
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium

# Expose the app on port 7860 (Hugging Face Spaces default)
ENV PORT=7860
ENV QUIZ_SECRET=s3cr3t-Quiz-2025-XYZ

# Run the Flask app
CMD ["python", "server.py"]
