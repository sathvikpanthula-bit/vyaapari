FROM python:3.10-slim

WORKDIR /app

# Since Render is already inside the backend directory, 
# requirements.txt and all code files are sitting right here!
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the files from this folder directly into /app
COPY . .

# Explicitly make sure Python checks /app for your modules
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
