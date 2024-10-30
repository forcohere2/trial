# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Install Python 3.11 and other necessary dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    libreoffice libreoffice-writer \
    ghostscript tesseract-ocr \
    tesseract-ocr-hin tesseract-ocr-guj tesseract-ocr-san \
    libfontconfig1 \
    libcairo2 \
    libjpeg-turbo8 \
    wget \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as the default Python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install pdf2htmlEX from .deb package
RUN wget https://github.com/pdf2htmlEX/pdf2htmlEX/releases/download/v0.18.8.rc1/pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.deb \
    && apt-get install -y ./pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.deb \
    && rm pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.deb

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Define environment variable
ENV NAME=DocumentViewer

# Run app.py when the container launches
CMD ["python3", "app.py"]
