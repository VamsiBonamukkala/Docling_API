FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        docling \
        spacy

# Expose the application port
EXPOSE 8998

# Start the application
CMD ["python3", "app.py", "--host", "0.0.0.0", "--port", "8998"]
