import requests
import json
from parladata.models import Speech, Session

def exportSpeeches():

    speeches = Speech.objects.all()

    i = 0

    for speech in speeches:
        output = [{
            'id': 'g' + str(speech.id),
            'speaker_i': speech.speaker.id,
            'session_i': speech.session.id,
            'org_i': speech.session.organization.id,
            'datetime_dt': speech.start_time.isoformat(),
            'content_t': speech.content,
            'tip_t': 'govor'
        }]

        if speech.party.classification == u'poslanska skupina':
            output[0]['party_i'] = speech.party.id

        output = json.dumps(output)

        if i%100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true', data=output, headers={'Content-Type': 'application/json'})

            print r.text

        else:
             r = requests.post('http://127.0.0.1:8983/solr/knedl/update', data=output, headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1

def getSessionContent(session):

    megastring = u''

    for speech in session.speech_set.all():
        megastring = megastring + ' ' + speech.content

    return megastring

def exportSessions():

    sessions = Session.objects.all()

    i = 0

    for session in sessions:
        output = [{
            'id': 's' + str(session.id),
            'org_i': session.organization.id,
            'datetime_dt': session.start_time.isoformat(),
            'content_t': getSessionContent(session),
            'tip_t': 'seja'
        }]

        output = json.dumps(output)

        if i%100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true', data=output, headers={'Content-Type': 'application/json'})

            print r.text

        else:
             r = requests.post('http://127.0.0.1:8983/solr/knedl/update', data=output, headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1
