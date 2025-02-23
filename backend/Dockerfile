FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    libmagic1 \
    libmagic-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Make start script executable
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"] 