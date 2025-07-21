# Use official Python image
FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y ca-certificates
RUN pip install truststore
RUN python -c "import truststore; truststore.inject_into_ssl()"

COPY . .

EXPOSE 8080

ARG ENTRYPOINT=app.main:app
ENV ENTRYPOINT=$ENTRYPOINT

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]