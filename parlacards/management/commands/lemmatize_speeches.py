from django.core.management.base import BaseCommand, CommandError
from parladata.models.speech import Speech

class Command(BaseCommand):
    help = 'Lemmatizes all speeches'

    def handle(self, *args, **options):
        speeches = Speech.objects.all()
        speech_count = speeches.count()

        print(f'Lemmatizing {speech_count} speeches ...')

        for i, speech in enumerate(speeches):
            speech.lemmatize_self()

            if i % 10 == 0:
                print(f'Done with {i} speeches ...')
        
        print('Done.')
