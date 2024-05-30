# fastapi/Dockerfile
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-it script
# COPY wait-for-it.sh /app/

# Copy the application code
COPY . ./fonteapi

# Expose port 8000
EXPOSE 8000

# Command to run the application
# CMD ["./wait-for-it.sh", "postgres-fonte", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "fonteapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
