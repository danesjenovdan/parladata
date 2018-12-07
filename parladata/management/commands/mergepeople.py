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
        self.stdout.write('\n')

        # check if real person exists
	try:
            real_person = Person.objects.get(id=int(options['original'][0]))
	except Person.DoesNotExist:
            raise CommandError('No real person found')

        # check if fake people exist
        if Person.objects.filter(id__in=[int(person_id) for person_id in options['fake']]).count() > 0:
            fake_people = Person.objects.filter(id__in=[int(person_id) for person_id in options['fake']])
        else:
            raise CommandError('No fake people found')

        # deal with ballots
        self.stdout.write('Real person has %d ballots.' % real_person.ballot_set.all().count())
        for fake_person in fake_people:
            self.stdout.write('Fake person %d has %d ballots.' % (fake_person.id, fake_person.ballot_set.all().count()))
            self.stdout.write('Moving ballots to real person...')
            for ballot in fake_person.ballot_set.all():
                ballot.voter = real_person
                ballot.save()
            self.stdout.write('Done with moving.')

        self.stdout.write('\n')

        self.stdout.write('Real person has %d speeches.' % real_person.speech_set.all().count())
        for fake_person in fake_people:
            self.stdout.write('Fake person %d has %d speeches.' % (fake_person.id, fake_person.speech_set.all().count()))
            self.stdout.write('Moving speeches to real person...')
            for speech in fake_person.speech_set.all():
                speech.speaker = real_person
                speech.save()
            self.stdout.write('Done with moving.')

        self.stdout.write('\n')
        self.stdout.write('DONE')
