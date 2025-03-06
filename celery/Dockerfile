# Use an official Python runtime as base
FROM python:3.10

# Set the working directory in the container
WORKDIR /celery

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set environment variables
ENV REDIS_BROKER=redis://redis:6379/0
ENV MONGO_URI=mongodb://mongodb:27017/your_database_name

# Start Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]