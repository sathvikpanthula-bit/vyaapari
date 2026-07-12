FROM python:3.10-slim

WORKDIR /app

# Since Render is already inside the backend folder, 
# requirements.txt is right here in the root!
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the backend files directly into the container
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
