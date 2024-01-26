# python base image
FROM python:3.9

# Workdir for output
WORKDIR /app

# Copy requirements.txt to workdir
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files
COPY . .

# Run API on container port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]