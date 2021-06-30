from django.core.management.base import BaseCommand, CommandError
from parladata.models import Vote

class Command(BaseCommand):
    help = 'Set result to votes without result'

    """
    relativno navadno večino: (večina prisotnih poslancev; najpogostejši način odločanja),
    absolutno navadno večino: (vsaj 46 glasov poslancev),
    relativno kvalificirano večino: (2/3 prisotnih poslancev) ali
    absolutno kvalificirano večino: (vsaj 60 glasov poslancev).
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--majority',
            nargs=1,
            help='Type if majority [relative_normal, absolute_normal]',
        )

    def handle(self, *args, **options):
        self.stdout.write('Start setting results')

        majority = options['original'][0]

        for vote in Vote.objects.filter(result=None):
            if majority == 'absolute_normal':
                final_result = self.get_result_for_absolute_normal_majority(vote)
            else:
                final_result = self.get_result_for_relative_normal_majority(vote)

            motion = vote.motion
            motion.result = final_result
            motion.save()
            vote.result = final_result
            vote.save()
            self.stdout.write('setting vote: ' + vote.name + ' as accepted' if final_result else 'as rejected')

        self.stdout.write('\n')
        self.stdout.write('DONE')


    def get_result_for_relative_normal_majority(self, vote):
        options = vote.get_option_counts()
        return options['for'] > options['against']

    def get_result_for_absolute_normal_majority(self, vote):
        options = vote.get_option_counts()
        return options['for'] > (sum(options.values())/2 + 1)



