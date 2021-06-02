from django.core.management.base import BaseCommand, CommandError

from parladata.models.organization import Organization
from parlacards.scores.seed import calculate_sparse_scores

class Command(BaseCommand):
    help = 'Seeds sparse scores'

    def handle(self, *args, **options):
        main_organization = Organization.objects.order_by('id').first()

        calculate_sparse_scores(main_organization)
