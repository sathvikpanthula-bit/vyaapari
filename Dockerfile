FROM python:3.10-slim

WORKDIR /app

# 1. Copy the requirements file directly from the backend folder and install it
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the entire repository content into /app
COPY . .

# 3. Change our active working directory straight to the backend folder
WORKDIR /app/backend

# 4. Explicitly include the backend directory in Python's search paths
ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
