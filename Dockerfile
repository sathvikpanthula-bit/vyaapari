FROM python:3.10-slim

WORKDIR /app

# 1. Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the entire backend folder contents straight into /app
# This moves main.py and routers into the exact same folder level!
COPY . .

EXPOSE 8000

# 3. Explicitly tell Python that the current folder is part of its search path
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
