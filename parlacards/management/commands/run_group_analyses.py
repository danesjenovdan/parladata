from django.core.management.base import BaseCommand

from parlacards.scores.update import force_run_group_analyses

from datetime import datetime


class Command(BaseCommand):
    help = "Run group analyses for a given time."

    def add_arguments(self, parser):
        parser.add_argument("--start_time", type=str, default="")

    def handle(self, *args, **options):

        input_timestamp = options["start_time"]
        if input_timestamp:
            timestamp = datetime.fromisoformat(input_timestamp)
        else:
            timestamp = datetime.now()

        force_run_group_analyses(timestamp, self.stdout.write)
