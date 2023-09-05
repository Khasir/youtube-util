# See: https://cloud.google.com/run/docs/tips/python

FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 4 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD python -m gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 app:app
