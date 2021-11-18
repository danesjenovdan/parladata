from django.core.management.base import BaseCommand, CommandError
from parladata.models import Medium


media = [
    'https://www.pravda.com.ua/',
    'https://lb.ua/',
    'https://nv.ua/ukr',
    'https://glavcom.ua/',
    'https://suspilne.media/',
    'https://www.ukrinform.ua/',
    'https://zn.ua/ukr/',
    'https://censor.net/',
    'https://www.liga.net/ua',
]


class Command(BaseCommand):
    help = 'Add default UA media'

    def handle(self, *args, **options):
        self.stdout.write('About to start adding default UA media ...')

        for medium in media:
            self.stdout.write(f'\t{medium}')
            Medium.objects.create(
                name=medium,
                url=medium,
            )

        self.stdout.write('Done')
