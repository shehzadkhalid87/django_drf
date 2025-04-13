from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from decouple import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTIN GS_MODULE', 'aia_project.settings')

app = Celery('aia_project')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all applications listed in INSTALLED_APPS
app.autodiscover_tasks()

# Optional configuration settings
app.conf.update(
    broker_url=config("BROKER_URL"),  # Redis as the broker
    result_backend=config("RESULT_URL"),  # Redis as the backend for task results
    result_expires=int(config("EXPIRE_IN")),  # Task results expiration time
)
