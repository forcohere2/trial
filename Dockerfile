# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install dependencies for OCR, LibreOffice, Tesseract, and curl, then clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice libreoffice-writer \
    ghostscript tesseract-ocr \
    tesseract-ocr-hin tesseract-ocr-guj tesseract-ocr-san \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Define environment variable
ENV NAME=DocumentViewer

# Run app.py when the container launches
CMD ["python", "app.py"]