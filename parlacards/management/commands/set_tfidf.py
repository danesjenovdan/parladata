from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Set TFIDF'

    def handle(self, *args, **options):
        self.stdout.write('Start setting TFIDF')

        self.stdout.write('PASS')



