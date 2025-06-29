# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables (optional: can also be done in docker-compose or CLI)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Create volume locations if necessary
RUN mkdir -p downloads history data logs

# Expose the port Flask uses
EXPOSE 5000

# Run the app
CMD ["flask", "run"]
