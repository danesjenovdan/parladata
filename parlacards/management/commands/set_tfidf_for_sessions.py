from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.tfidf import save_sessions_tfidf_between
from parladata.models.organization import Organization

from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Set TFIDF for sessions'

    def handle(self, *args, **options):
        self.stdout.write('Start setting TFIDF')
        playing_field = Organization.objects.first()
        save_sessions_tfidf_between(playing_field, datetime_from=datetime.now()-timedelta(days=100), datetime_to=datetime.now())



