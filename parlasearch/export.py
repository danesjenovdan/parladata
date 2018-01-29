import requests
import json
from parladata.models import Person, Speech, Session, Organization, Vote
from datetime import datetime

SOLR_URL = 'http://127.0.0.1:8983/solr/knedl'
PS = 'poslanska skupina'


def exportSpeeches():

    # get all valid speeches
    speeches = Speech.getValidSpeeches(datetime.now())

    # get all ids from solr
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&rows=100000000")
    indexes = a.json()["response"]["docs"]

    # find ids of speeches and remove g from begining of id string
    idsInSolr = [int(line["id"].replace('g', ''))
                 for line
                 in indexes if "g" in line["id"]]

    i = 0

    for speech in speeches.exclude(id__in=idsInSolr):
        output = [{
            'id': 'g' + str(speech.id),
            'speaker_i': speech.speaker.id,
            'session_i': speech.session.id,
            'org_i': speech.session.organization.id,
            'party_i': speech.party_id,
            'datetime_dt': speech.start_time.isoformat(),
            'content_t': speech.content,
            'tip_t': 'govor'
        }]

        if speech.party.classification == u'poslanska skupina':
            output[0]['party_i'] = speech.party.id

        output = json.dumps(output)

        if i % 100 == 0:
            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})


        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def getSessionContent(session):

    megastring = u''
    speeches = Speech.getValidSpeeches(datetime.now()).filter(session=session)
    for speech in speeches:
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
            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def exportSession(session_id):

    session = Session.objects.filter(id=session_id)
    if not session:
        print("session with this id didn't exists")
        return "session with this id didn't exists"
    else:
        session = session[0]

    output = [{
        'id': 's' + str(session.id),
        'org_i': session.organization.id,
        'datetime_dt': session.start_time.isoformat(),
        'content_t': getSessionContent(session),
        'sklic_t': 'VII',
        'tip_t': 'seja'
    }]

    output = json.dumps(output)

    url = SOLR_URL + '/update?commit=true'
    r = requests.post(url,
                      data=output,
                      headers={'Content-Type': 'application/json'})

    return 'session speeches was stored'


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
            r = requests.post(SOLR_URL + '/update?commit=true',
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post(SOLR_URL + '/update',
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

    organizations = Organization.objects.filter(classification=PS)

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
            r = requests.post(SOLR_URL + '/update?commit=true',
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post(SOLR_URL + '/update',
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
            r = requests.post(SOLR_URL + '/update?commit=true',
                              data=output,
                              headers={'Content-Type': 'application/json'})

            print r.text

        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1


def exportAll():
    print "deleteing non valid speeches"
    deleteNonValidSpeeches()
    print 'exporting speeches'
    exportSpeeches()
    #print 'exporting sessions'
    #exportSessions()
    # print 'exporting people_speeches'
    # exportPeopleSpeeches()
    # print 'exporting party speeches'
    # exportPartySpeeches()
    print 'exporting votes'
    exportVotes()

    return 'all done'


def deleteNonValidSpeeches():
    # get all ids from solr
    a = requests.get(SOLR_URL + "/select?wt=json&q=id:*&fl=id&rows=100000000")
    indexes = a.json()["response"]["docs"]

    # find ids of speeches and remove g from begining of id string
    idsInSolr = [int(line["id"].replace('g', ''))
                 for line
                 in indexes if "g" in line["id"]]

    # get all valid speeches
    validSpeeches = Speech.getValidSpeeches(datetime.now())
    idsInData = validSpeeches.values_list("id", flat=True)

    # find ids of speeches in solr for delete
    idsForDelete = list(set(idsInSolr) - set(idsInData))
    idsForDelete = ['g'+str(gid) for gid in idsForDelete]

    # prepare query data
    data = {'delete': idsForDelete
            }

    r = requests.post(SOLR_URL + '/update?commit=true',
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    print r.text

    return


def exportAllSpeechesOfPerson(person_id):

    # get all valid speeches
    speeches = Speech.getValidSpeeches(datetime.now()).filter(speaker_id=person_id)

    i = 0

    for speech in speeches:
        output = [{
            'id': 'g' + str(speech.id),
            'speaker_i': speech.speaker.id,
            'session_i': speech.session.id,
            'org_i': speech.session.organization.id,
            'party_i': speech.party_id,
            'datetime_dt': speech.start_time.isoformat(),
            'content_t': speech.content,
            'tip_t': 'govor'
        }]

        if speech.party.classification in [u'poslanska skupina', u'ministrstvo']:
            output[0]['party_i'] = speech.party.id

        output = json.dumps(output)

        if i % 100 == 0:
            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})


        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1

    return 1