from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.tfidf import save_sessions_tfidf_for_fresh_sessions
from parlacards.utils import get_playing_fields
from parladata.models.organization import Organization
from datetime import datetime


class Command(BaseCommand):
    help = 'Set TFIDF for sessions'

    def handle(self, *args, **options):
        self.stdout.write('Start setting TFIDF')
        playing_field = get_playing_fields(datetime.now())
        save_sessions_tfidf_for_fresh_sessions(playing_field,)
