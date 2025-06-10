# Use official Python image
FROM python:3.13

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y ca-certificates
RUN pip install truststore
RUN python -c "import truststore; truststore.inject_into_ssl()"

# Copy code source: backend, dest: mnt
COPY . .

# Expose port (Cloud Run default)
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
