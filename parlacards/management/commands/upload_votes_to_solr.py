import json

import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from parladata.models.vote import Vote
from parlacards.serializers.vote import SessionVoteSerializer

from datetime import datetime, timedelta

# TODO move this out of here
def commit_to_solr(commander, output):
    url = settings.SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s votes to %s' % (str(len(output)), url))
    data = json.dumps(output)
    print (requests.post(url,
        data=data,
        headers={
            'Content-Type': 'application/json'
        }
    ).content)

# TODO move this out of here
def delete_invalid_votes(vote_ids_in_solr):
    vote_ids = list(Vote.objects.all().values_list('id', flat=True))

    ids_to_delete = list(set(vote_ids_in_solr) - set(vote_ids))
    if bool(ids_to_delete):
        solr_ids_to_delete = ['vote_' + str(i) for i in ids_to_delete]

        data = {
            'delete': solr_ids_to_delete
        }

        solr_response = requests.post(settings.SOLR_URL + '/update?commit=true',
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json'
            }
        )

class Command(BaseCommand):
    help = 'Uploads all votes to solr'

    def handle(self, *args, **options):
        # get IDs from SOLR so we don't upload
        # vote already there
        yesterday = datetime.now() - timedelta(days=1)
        url = settings.SOLR_URL + '/select?wt=json&q=type:vote&fl=vote_id&rows=100000000'
        self.stdout.write(f'Getting all IDs from {url} ...')
        solr_response = requests.get(url)
        try:
            docs = solr_response.json()['response']['docs']
            ids_in_solr = [
                doc['vote_id'] for
                doc in
                solr_response.json()['response']['docs'] if
                'vote_id' in doc
            ]
        except:
            ids_in_solr = []

        # delete invalid votes
        self.stdout.write('Deleting invalid votes ...')
        delete_invalid_votes(ids_in_solr)

        votes = Vote.objects.exclude(id__in=ids_in_solr).prefetch_related('motion', 'motion__session')

        updated_votes = Vote.objects.filter(updated_at__gte=yesterday).prefetch_related('motion', 'motion__session')
        votes = set(list(votes) + list(updated_votes))

        self.stdout.write(f'Uploading {len(votes)} votes to solr ...')
        output = []
        for i, vote in enumerate(votes):
            output.append({
                'term': vote.motion.session.mandate.id,
                'type': 'vote',
                'id': 'vote_' + str(vote.id),
                'vote_id': vote.id,
                'session_id': vote.motion.session.id,
                'org_id': vote.motion.session.organization.id,
                'start_time': vote.timestamp.isoformat(),
                'content': vote.name,
                #'results_json': SessionVoteSerializer(vote).data,
            })

            if (i > 0) and (i % 100 == 0):
                commit_to_solr(self, output)
                output = []

        if bool(output):
            commit_to_solr(self, output)
