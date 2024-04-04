from django.core.management.base import BaseCommand

from parlacards.scores.update import run_analyises_for_new_data

from datetime import datetime


class Command(BaseCommand):
    help = "Run daily update for new data."

    def add_arguments(self, parser):
        parser.add_argument("--start_time", type=str, default="")

    def handle(self, *args, **options):

        input_timestamp = options["start_time"]
        if input_timestamp:
            timestamp = datetime.fromisoformat(input_timestamp)
        else:
            timestamp = datetime.now()

        run_analyises_for_new_data(timestamp)
