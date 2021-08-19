
from django.core.management.base import BaseCommand, CommandError

from importlib import import_module

from parladata.models.task import Task

from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Run '

    def handle(self, *args, **options):
        tasks = Task.objects.filter(started_at__isnull=True).order_by('created_at')
        for task in tasks:
            try:
                tasks_module = import_module('parladata.tasks')
                task_method = getattr(tasks_module, task.name)
                task.started_at = datetime.now()
                task.save()
                task_method(**task.payload)
                task.finished_at = datetime.now()
                task.save()
            except Exception as e:
                self.stdout.write(e)
                task.errored_at = datetime.now()
                task.save()

