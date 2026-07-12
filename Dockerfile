FROM python:3.10-slim

WORKDIR /app

# Copy the requirements file from the current directory and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into the /app directory
COPY . .

# Force Python to look both in /app and inside a backend directory if it exists
ENV PYTHONPATH="/app:/app/backend"

# Start the application by letting Uvicorn try both common path styles
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
