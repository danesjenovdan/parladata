from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parladata_project.settings')

app = Celery('parladata_project')
app.config_from_object('django.conf:settings', namespace='CELERYPARLADATA')
app.autodiscover_tasks()
