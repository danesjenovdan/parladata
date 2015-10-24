import requests
import json
from parladata.models import Speech

def export():
    i = 0

    while i < 10000:
        speech = Speech.objects.all()[i]
        output = [{
            'id': 'g' + str(speech.id),
            'speaker_i': speech.speaker.id,
            'session_i': speech.session.id,
            'org_i': speech.session.organization.id,
#            'datetime_dt': speech.start_time,
            'party_i': speech.party.id,
            'content_t': speech.content
        }]

        output = json.dumps(output)

        i = i + 1

        if i%100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true', data=output, headers={'Content-Type': 'application/json'})
        else:
             r = requests.post('http://127.0.0.1:8983/solr/knedl/update', data=output, headers={'Content-Type': 'application/json'})
        print r.text
        
    return 1
        
        
