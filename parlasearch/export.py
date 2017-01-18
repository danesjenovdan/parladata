import requests
import json
from parladata.models import Person, Speech, Session, Organization, Vote
from datetime import datetime


def exportSpeeches():

    speeches = Speech.getValidSpeeches(datetime.now())

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

        if i % 100 == 0:
            url = 'http://127.0.0.1:8983/solr/knedl/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

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
            'sklic_t': 'VII',
            'tip_t': 'seja'
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            url = 'http://127.0.0.1:8983/solr/knedl/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def getPersonContent(person):

    megastring = u''

    for speech in person.speech_set.all():
        megastring = megastring + ' ' + speech.content

    return megastring


def exportPeopleSpeeches():

    people = Person.objects.all()

    i = 0

    for person in people:
        output = [{
            'id': 'p' + str(person.id),
            'content_t': getPersonContent(person),
            'sklic_t': 'VII',
            'tip_t': 'poslanec'
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true',
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def getOrganizationContent(organization):

    megastring = u''

    for speech in organization.speech_set.all():
        megastring = megastring + ' ' + speech.content

    return megastring


def exportPartySpeeches():

    organizations = Organization.objects.filter(classification='poslanska skupina')

    i = 0

    for organization in organizations:
        output = [{
            'id': 'ps' + str(organization.id),
            'content_t': getOrganizationContent(organization),
            'sklic_t': 'VII',
            'tip_t': 'ps'
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true',
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def exportVotes():

    votes = Vote.objects.all()

    i = 0

    for vote in votes:
        output = [{
            'id': 'v' + str(vote.id),
            'motionid_i': str(vote.motion.id),
            'voteid_i': str(vote.id),
            'content_t': vote.motion.text,
            'sklic_t': 'VII',
            'tip_t': 'v'
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update?commit=true', data=output, headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post('http://127.0.0.1:8983/solr/knedl/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def exportAll():

    print 'exporting speeches'
    exportSpeeches()
    print 'exporting sessions'
    exportSessions()
    # print 'exporting people_speeches'
    # exportPeopleSpeeches()
    # print 'exporting party speeches'
    # exportPartySpeeches()
    print 'exporting votes'
    exportVotes()

    return 'all done'
