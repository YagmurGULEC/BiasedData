# celery.py
from celery import Celery
from dotenv import load_dotenv,find_dotenv
import os

celery_app = Celery(
    "myapp",
    backend=os.getenv("CELERY_BROKER_URL"),  # Use the service name 'redis'
    broker=os.getenv("CELERY_BROKER_URL"),  # Use the service name 'redis'
    include=['app.tasks']
)