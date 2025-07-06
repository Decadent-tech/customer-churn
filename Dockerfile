# Use a Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
