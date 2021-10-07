import json

import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from parladata.models.speech import Speech

# TODO move this out of here
def commit_to_solr(commander, output):
    url = settings.SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s speeches to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
        data=data,
        headers={
            'Content-Type': 'application/json'
        }
    )

# TODO move this out of here
def delete_invalid_speeches(speech_ids_in_solr):
    valid_speech_ids = Speech.objects.filter_valid_speeches().values_list(
        'id',
        flat=True
    )

    ids_to_delete = list(set(speech_ids_in_solr) - set(valid_speech_ids))

    solr_ids_to_delete = ['speech_' + str(i) for i in ids_to_delete]

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
    help = 'Uploads all speeches to solr'

    def handle(self, *args, **options):
        # get IDs from SOLR so we don't upload
        # speeches already there
        url = settings.SOLR_URL + '/select?wt=json&q=type:speech&fl=speech_id&rows=100000000'
        self.stdout.write(f'Getting all IDs from {url} ...')
        solr_response = requests.get(url)
        try:
            docs = solr_response.json()['response']['docs']
            ids_in_solr = [
                doc['speech_id'] for
                doc in
                solr_response.json()['response']['docs'] if
                'speech_id' in doc
            ]
        except:
            ids_in_solr = []

        # delete invalid speeches
        self.stdout.write('Deleting invalid speeches ...')
        delete_invalid_speeches(ids_in_solr)

        speeches = Speech.objects.exclude(id__in=ids_in_solr)
        self.stdout.write(f'Uploading {speeches.count()} speeches to solr ...')
        output = []
        for i, speech in enumerate(speeches):
            maybe_party = speech.speaker.parliamentary_group_on_date(speech.start_time)
            output.append({
                'type': 'speech',
                'id': 'speech_' + str(speech.id),
                'speech_id': speech.id,
                'person_id': speech.speaker.id,
                'start_time': speech.start_time.isoformat(),
                'content': speech.content,
                'term': speech.session.mandate.id,
                'party_id': maybe_party.id if maybe_party else None, # TODO rename to group_id
                # 'term_id': speech.session.mandate.id
            })

            if (i > 0) and (i % 100 == 0):
                commit_to_solr(self, output)
                output = []

        if bool(output):
            commit_to_solr(self, output)
