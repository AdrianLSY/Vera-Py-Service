FROM python:3.13.7-alpine3.22

# Set Python to use UTF-8 encoding
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create a working directory
WORKDIR /auth

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies directly to system Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (we skip having to install dependencies since its done in the previous step)
COPY . .

# Run the test script using system Python
CMD ["python", "entrypoint.py"]
