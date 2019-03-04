from django.core.management.base import BaseCommand, CommandError
from parladata.models import Vote

class Command(BaseCommand):
    help = 'Set result to votes without result'

    def handle(self, *args, **options):
        self.stdout.write('Start setting results')

        for vote in Vote.objects.filter(result=None):
            results = vote.getResult()
            print(vote.ballot_set.all().filter(option="against").count())
            if vote.ballot_set.all().filter(option="against").count()>61:
                motion=vote.motion
                motion.result=1
                motion.save()
                self.stdout.write('setting vote: ' + vote.name + ' with results ' + str(results) + ' as accepted')

        for vote in Vote.objects.filter(result=None):
            if vote.ballot_set.all().filter(option="against").count() >= vote.ballot_set.all().filter(option="for").count():
                motion=vote.motion
                motion.result=0
                motion.save()
                self.stdout.write('setting vote: ' + vote.name + ' with results ' + str(results) + ' as rejected')

        self.stdout.write('\n')
        self.stdout.write('DONE')
