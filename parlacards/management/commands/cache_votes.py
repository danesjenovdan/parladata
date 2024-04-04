from django.core.management.base import BaseCommand

from parladata.models.vote import Vote
from parlacards.serializers.vote import VoteSerializer

from datetime import datetime


class Command(BaseCommand):
    help = "Caches all the votes if they are not already cached."

    def handle(self, *args, **options):
        for vote in Vote.objects.all():
            print(f"Caching vote with id {vote.id}")
            serializer = VoteSerializer(vote, context={"date": datetime.today()})
            # call serializer.data to actually cache everything
            serializer.data
