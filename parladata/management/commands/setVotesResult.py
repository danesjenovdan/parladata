from django.core.management.base import BaseCommand, CommandError
from parladata.models import Vote

class Command(BaseCommand):
    help = 'Set result to votes without result'

    def handle(self, *args, **options):
        self.stdout.write('Start setting results')


        for vote in Vote.objects.filter(result=None):
            final_result = None
            results = vote.getResult()
            if results['absent'] > 44:
                final_result = 0
            elif results['for'] > results['against']:
                final_result = 1
            else:
                final_result = 0
            motion = vote.motion
            motion.result = final_result
            motion.save()
            self.stdout.write('setting vote: ' + vote.name + ' with results ' + str(results) + ' as accepted' if final_result else 'as rejected')

        self.stdout.write('\n')
        self.stdout.write('DONE')
