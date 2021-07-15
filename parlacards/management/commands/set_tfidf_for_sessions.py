from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.tfidf import save_sessions_tfidf_for_fresh_sessions
from parladata.models.organization import Organization


class Command(BaseCommand):
    help = 'Set TFIDF for sessions'

    def handle(self, *args, **options):
        self.stdout.write('Start setting TFIDF')
        playing_field = Organization.objects.first()
        save_sessions_tfidf_for_fresh_sessions(playing_field,)
