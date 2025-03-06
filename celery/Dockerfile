# Use an official Python runtime as base
FROM python:3.10

# Set the working directory in the container
WORKDIR /celery

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]

#CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--beat"]
# Run Celery worker and beat in a single container
#CMD ["bash", "-c", "celery -A tasks worker --loglevel=info & celery -A tasks beat --scheduler celery.beat.schedulers.PersistentScheduler --loglevel=info"]
