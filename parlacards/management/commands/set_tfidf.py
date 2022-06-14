from django.core.management.base import BaseCommand, CommandError

from parladata.models import Organization
from parlacards.scores.tfidf import save_groups_tfidf, save_people_tfidf
from parlacards.utils import get_playing_fields

from datetime import datetime

class Command(BaseCommand):
    help = 'Set TFIDF'

    def handle(self, *args, **options):
        self.stdout.write('Start setting TFIDF for groups')

        playing_field = get_playing_fields(datetime.now())

        save_groups_tfidf(playing_field, timestamp=datetime.now())

        self.stdout.write('Start setting TFIDF for people')
        save_people_tfidf(playing_field, timestamp=datetime.now())

        self.stdout.write('Done')
