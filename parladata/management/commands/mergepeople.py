from django.core.management.base import BaseCommand, CommandError
from parladata.models import Person

class Command(BaseCommand):
    help = 'Merges people together'

    def add_arguments(self, parser):
        parser.add_argument(
            '--original',
            nargs=1,
            help='Original person',
        )

        parser.add_argument(
            '--fake',
            nargs='+',
            help='Fake people',
        )

    def handle(self, *args, **options):
        self.stdout.write('Real person id: %s' % options['original'][0])
        self.stdout.write('Fake people ids: %s' % ', '.join(options['fake']))

        real_person = Person.objects.get(id=int(options['original'][0]))
        fake_people = Person.objects.filter(id__in=[int(person_id) for person_id in options['fake']])

        self.stdout.write('Real person has %d ballots.' % real_person.ballot_set.all().count())
        for fake_person in fake_people:
            self.stdout.write('Fake person %d has %d ballots.' % (fake_person.id, fake_person.ballot_set.all().count()))
        
        self.stdout.write('Real person has %d speeches.' % real_person.speech_set.all().count())
        for fake_person in fake_people:
            self.stdout.write('Fake person %d has %d speeches.' % (fake_person.id, fake_person.speech_set.all().count()))

        self.stdout.write('DONE')