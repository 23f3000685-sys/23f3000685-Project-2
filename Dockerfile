FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Create app directory
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server.py"]
