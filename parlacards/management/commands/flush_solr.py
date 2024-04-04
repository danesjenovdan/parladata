from django.core.management.base import BaseCommand

from parlacards.solr import delete_solr_documents

from datetime import datetime


class Command(BaseCommand):
    help = "Delete all documents from solr"

    def handle(self, *args, **options):
        delete_solr_documents()
