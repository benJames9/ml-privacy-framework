# python base image
# FROM python:3.9
FROM pytorch/pytorch:latest

# Workdir for output
WORKDIR /app

# Copy requirements.txt to workdir
COPY requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy files to workdir
COPY . . 

# Run API on container port 8000
CMD uvicorn main:app --host 0.0.0.0 --port 8000
