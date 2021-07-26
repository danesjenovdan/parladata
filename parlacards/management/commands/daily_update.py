from django.core.management.base import BaseCommand, CommandError

from parladata.models.organization import Organization
from parlacards.scores.update import run_analyises_for_new_data

class Command(BaseCommand):
    help = 'Seeds sparse scores'

    def handle(self, *args, **options):
        run_analyises_for_new_data()
