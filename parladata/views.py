# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from datetime import date, datetime, timedelta
from parladata.models import *
from django.db.models import Q
from django.forms.models import model_to_dict
import json
import simplejson
from utils import *
import requests
from raven.contrib.django.raven_compat.models import client
from collections import OrderedDict
from django.conf import settings
from django.utils.encoding import smart_str
from taggit.models import Tag
from django.shortcuts import get_object_or_404


"""return all ballots and speaches agregated by date

id: id of person
"""
def getActivity(request, person_id):

    def appendBallot(data, b):
        tempBallot = dict()
        tempBallot['type'] = 'ballot'
        tempBallot['date'] = str(b.vote.start_time.date())
        tempBallot['option'] = b.option
        tempBallot['result'] = b.vote.result
        tempBallot['vote_id'] = b.vote.id
        tempBallot['vote_name'] = b.vote.name
        #motion is currently empty
        #tempBallot.text = b.vote.motion.recap
        if tempBallot['date'] in data:
            data[tempBallot['date']].append(tempBallot)
        else:
            data[tempBallot['date']] = [tempBallot]

    def appendSpeech(data, s):
        tempSpeech = dict()
        tempSpeech['type'] = "speech"
        tempSpeech['date'] = str(s.start_time.date())
        tempSpeech['session_name'] = s.session.name
        tempSpeech['session_id'] = s.session.id
        tempSpeech['speech_id'] = s.id
        if tempSpeech['date'] in data:
            data[tempSpeech['date']].append(tempSpeech)
        else:
            data[tempSpeech['date']] = [tempSpeech]

    data = dict()
    person = Person.objects.filter(id=person_id)
    if person:
        ballots = Ballot.objects.filter(voter=person).order_by('vote__start_time');
        speeches = Speech.objects.filter(speaker=person).order_by('start_time');

        for b in ballots:
            appendBallot(data, b)
        for s in speeches:
            appendSpeech(data, s)
    data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))

    data_list = [data[x] for x in data]
    return JsonResponse(data_list, safe=False)

'''
MP = Members of parlament
#Function: git config
'''
def getMPs(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().today()
    data = []

    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    for i in getMPObjects(fdate):
        districts = ''

        if i.districts:
            districts = i.districts.all().values_list("name", flat=True)
            if not districts:
                districts = None
	    else:
		districts = [smart_str(dist) for dist in districts]
        membership = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None))
        #membership = Membership.objects.filter(person = i, organization=parliamentary_group)

        data.append({'id': i.id, 'name':i.name,'membership':membership[0].organization.name, 'acronym':membership[0].organization.acronym,'classification':i.classification,'family_name':i.family_name,'given_name':i.given_name,'additional_name':i.additional_name,'honorific_prefix':i.honorific_prefix,'honorific_suffix':i.honorific_suffix,'patronymic_name':i.patronymic_name,'sort_name':i.sort_name,'email':i.email,'gender':i.gender,'birth_date':str(i.birth_date),'death_date':str(i.death_date),'summary':i.summary,'biography':i.biography,'image':i.image,'district':districts,'gov_url':i.gov_url.url,'gov_id':i.gov_id,'gov_picture_url':i.gov_picture_url,'voters':i.voters,'active':i.active,'party_id':membership[0].organization.id})
    print len(data)
    return  JsonResponse(data, safe=False)


# returns MP static data like PoliticalParty, age, ....
def getMPStatic(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = dict()
    for member in getMPObjects(fdate):
        if str(member.id) == str(person_id):
            groups = [{'name': membership.organization.name,
                       'id': membership.organization.id,
                       'acronym': membership.organization.acronym} for membership in member.memberships.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None)) if membership.organization.classification  in [u'poslanska skupina', u'nepovezani poslanec']]
            if not groups:
                return JsonResponse({})

            non_party_groups = [{'name': membership.organization.name, 'id': membership.organization.id} for membership in member.memberships.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None)) if membership.organization.classification not in [u'poslanska skupina', u'nepovezani poslanec']]

            for group in non_party_groups:
                groups.append(group)

            print groups
            # creates a list of all memberships of MP
#            for i in parliamentary_group:
#                groups.append(i.organization)
            # calcutaes age of MP
            try:
                birth_date = str(member.birth_date)
                age = date.today() - date(int(birth_date[:4]),
                                          int(birth_date[5:7]),
                                          int(birth_date[8:10]))
                age = age.days / 365
            except:
                client.captureException()
                age = None

            twitter = member.link_set.filter(tags__name__in=['tw'])
            facebook = member.link_set.filter(tags__name__in=['fb'])
            linkedin = member.link_set.filter(tags__name__in=['linkedin'])

            social_output = {}
            if len(twitter) > 0:
                social_output['twitter'] = twitter[0].url
            else:
                social_output['twitter'] = False
            if len(facebook) > 0:
                social_output['facebook'] = facebook[0].url
            else:
                social_output['facebook'] = False
            if len(linkedin) > 0:
                social_output['linkedin'] = linkedin[0].url
            else:
                social_output['linkedin'] = False

            district = list(member.districts.all().values_list('id',
                                                               flat=True))
            if not district:
                district = None

            # get functions in working bodies
            wbs = ['odbor',
                   'komisija',
                   'preiskovalna komisija']

            roles = ['predsednik',
                     'predsednica',
                     'podpredsednica',
                     'podpredsednik']

            trans_map = {'predsednik': 'president',
                         'predsednica': 'president',
                         'podpredsednica': 'vice_president',
                         'podpredsednik': 'vice_president'}

            wb = Organization.objects.filter(Q(classification__in=wbs) |
                                             Q(id=95))
            posts = Post.objects.filter(membership__person__id=person_id)
            mp = posts.filter(organization__in=wb, role__in=roles)
            person_functions = [{'org_id': role.organization.id,
                                 'role': trans_map[role.role]} for role in mp]

            groupz = [{'name': group['name'],
                       'id': group['id']} for group in groups[1:]]

            data = {
                'previous_occupation': member.previous_occupation,
                'education': member.education,
                'mandates': member.mandates,
                'party': groups[0]['name'],
                'acronym': groups[0]['acronym'],
                'party_id': groups[0]['id'],
                'district': district,
                'voters': member.voters,
                'age': age,
                'groups': groupz,
                'name': member.name,
                'social': social_output,
                'gov_id': member.gov_id,
                'gender': 'm' if member.gender == 'male' else 'f',
                'working_bodies_functions': person_functions,
            }

    return JsonResponse(data)

#return all Sessions
def getSessions(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()
    data = []
    sessions = Session.objects.filter(start_time__lte=fdate).order_by('-start_time')
    for i in sessions:
        data.append({'mandate': i.mandate,
                     'name': i.name,
                     'gov_id': i.gov_id,
                     'start_time': i.start_time,
                     'end_time': i.end_time,
                     'organization': i.organization.name,
                     'organization_id': i.organization.id,
                     'classification': i.classification,
                     'id': i.id,
                     'is_in_review': i.in_review,
                    })
    return JsonResponse(data, safe=False)


def getSessionsOfOrg(request, org_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()
    data = []
    sessions = Session.objects.filter(organization__id=org_id, start_time__lte=fdate).order_by('-start_time')
    for i in sessions:
        data.append({'mandate': i.mandate,
                     'name': i.name,
                     'gov_id': i.gov_id,
                     'start_time': i.start_time,
                     'end_time': i.end_time,
                     'organization': i.organization.name,
                     'organization_id': i.organization.id,
                     'classification': i.classification,
                     'id': i.id
                    })
    return JsonResponse(data, safe=False)

#return votes of MP
def getVotes(request, date_=None):
    return JsonResponse(getVotesDict(date_))

#return speech by id
def getSpeeches(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()
    speaker_list = Person.objects.filter(id=person_id)
    if len(speaker_list) > 0:
        speaker = speaker_list[0]

    speeches_queryset = Speech.objects.filter(speaker=speaker, start_time__lte=fdate)

    speeches = [{'content': speech.content, 'speech_id': speech.id} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


#return speech by id
def getSpeechesInRange(request, person_id, date_from, date_to):

    fdate = datetime.strptime(date_from, settings.API_DATE_FORMAT).date()
    tdate = datetime.strptime(date_to, settings.API_DATE_FORMAT).date()

    speaker = get_object_or_404(Person, id=person_id)

    speeches_queryset = Speech.objects.filter(speaker=speaker, start_time__lte=tdate, start_time__gte=fdate)

    speeches = [{'content': speech.content, 'speech_id': speech.id} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)

'''
PG = Parlamentary group

return list of member's id for each PG
'''
def getMembersOfPGs(request):
	parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
	members = Membership.objects.filter(Q(end_time=None) | Q(end_time__gt=datetime.now()), organization__in=parliamentary_group)
	data = {pg.id:[member.person.id for member in members.filter(organization=pg)] for pg in parliamentary_group}
	return JsonResponse(data)


'''
PG = Parlamentary group

return list of member's id for each PG, on specific date
'''
def getMembersOfPGsOnDate(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(Q(end_time__gte=fdate) | Q(end_time=None), Q(start_time__lte=fdate)|Q(start_time=None), organization__in=parliamentary_group)
    data = {pg.id:[member.person.id for member in members.filter(organization=pg)] for pg in parliamentary_group}
    return JsonResponse(data)


#get coalitions PGs
def getCoalitionPGs(request):
    coalition = Organization.objects.filter(classification="poslanska skupina", is_coalition="1").values_list("id", flat=True)
    oppo = Organization.objects.filter(classification="poslanska skupina")
    oppo = oppo.exclude(is_coalition="1").values_list("id", flat=True)
    return JsonResponse({'coalition': list(coalition), 'opposition': list(oppo)})

#return number of MP attended sessions
def getNumberOfMPAttendedSessions(request, person_id):
    data = {}
    allBallots = Ballot.objects.filter(option='za')
    for i in getMPObjects():
        data[i.id] = len(list(set(allBallots.filter(voter=i.id).values_list('vote__session', flat=True))))
    return JsonResponse(data[int(person_id)], safe=False)


def getNumberOfAllMPAttendedSessions(request, date_):
    fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date() + timedelta(days=1) - timedelta(minutes=1)
    data = {"sessions":{},"votes":{}}
    for member in getMPObjects(fdate):
        allOfHimS = list(set(Ballot.objects.filter(voter__id=member.id, vote__start_time__lte=fdate).values_list("vote__session",flat=True)))
        votesOnS = list(set(Ballot.objects.filter(Q(option="kvorum")|Q(option="proti")|Q(option="za"), voter__id=member.id, vote__start_time__lte=fdate).values_list("vote__session",flat=True)))
        allOfHimV = list(set(Ballot.objects.filter(voter__id=member.id, vote__start_time__lte=fdate).values_list("vote",flat=True)))
        votesOnV = list(set(Ballot.objects.filter(Q(option="kvorum")|Q(option="proti")|Q(option="za"), voter__id=member.id, vote__start_time__lte=fdate).values_list("vote",flat=True)))
        try:
            data["sessions"][member.id] = float(len(votesOnS))/float(len(allOfHimS))*100
            data["votes"][member.id] = float(len(votesOnV))/float(len(allOfHimV))*100
        except:
            print member.id, " has not votes in this day"
    return JsonResponse(data)



#return all speeches of all MP
def getSpeechesOfMP(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    content = list(Speech.objects.filter(speaker__id = person_id, start_time__lte=fdate).values_list('content', flat=True))
    return JsonResponse(content, safe=False)


#return all speeches of all MP
def getSpeechesOfMPbyDate(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    dates=Speech.objects.filter(speaker__id = person_id, start_time__lte=fdate).order_by("start_time").dates("start_time", "day")
    content = [{"date":date.strftime(settings.API_DATE_FORMAT), "speeches": [speech.content for speech in Speech.objects.filter(Q(start_time__gte=date)|Q(start_time__lte=date+timedelta(days=1)), speaker__id = person_id)]} for date in dates]
    return JsonResponse(content, safe=False)


def getAllSpeeches(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()

    speeches_queryset = Speech.objects.filter(start_time__lte=fdate)

    speeches = [{'content': speech.content, 'speech_id': speech.id, 'speaker':speech.speaker.id, 'session_name':speech.session.name, 'session_id':speech.session.id,} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


def getAllSpeechesOfMPs(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()

    parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
    members = list(set(Membership.objects.filter(organization__in=parliamentary_group).values_list("person__id", flat=True)))

    speeches_queryset = Speech.objects.filter(speaker__in=members, start_time__lte=fdate)

    #speeches = [{'content': speech.content, 'speech_id': speech.id, 'speaker':speech.speaker.id, 'session_name':speech.session.name, 'session_id':speech.session.id,} for speech in speeches_queryset]
    
    #for speech in speeches:
    #    data.append(model_to_dict(speech, fields=[field.name for field in speech._meta.fields], exclude=[]))
    
    speeches = [model_to_dict(speech, fields=[field.name for field in speech._meta.fields], exclude=[]) for speech in speeches_queryset]
    return JsonResponse(speeches, safe=False)


def getMPParty(request, person_id):
    person = Person.objects.get(id=person_id)

    parties = [{'name': membership.organization.name, 'id': membership.organization.id, 'acronym': membership.organization.acronym} for membership in person.memberships.all() if membership.organization.classification == u'poslanska skupina']

    out = {'name': parties[0]['name'], 'id': parties[0]['id'], 'acronym': parties[0]['acronym']}

    return JsonResponse(out)

#returns number of seats in each parliamentary group
def getNumberOfSeatsOfPG(request, pg_id):
    value = dict()
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina",id = int(pg_id))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    data = {pg.id:len([member.person.id for member in members.filter(organization=pg)]) for pg in parliamentary_group}
    value = {int(pg_id):data[int(pg_id)]}
    return JsonResponse(value, safe=False)


#return basic info of parlament group
def getBasicInfOfPG(request, pg_id, date_):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()
    viceOfPG = []
    data = dict()
    listOfVotes = []
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina", id=pg_id)
    members = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), organization__id=parliamentary_group)

    if len(Post.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), membership__organization=parliamentary_group, label="v")) == 1:
        headOfPG = Post.objects.get(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), membership__organization=parliamentary_group, label="v").membership.person.id
    else:
        headOfPG = None

    if len(Post.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), membership__organization=parliamentary_group, label="namv")) > 0:
        for post in Post.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), membership__organization=parliamentary_group, label="namv"):
            
            viceOfPG.append(post.membership.person.id)
    else:
        viceOfPG = None
    
    numberOfSeats = len(members)

    for a in members:
        if a.person.voters != None:
            listOfVotes.append(a.person.voters)
        else:
            listOfVotes.append(0)
    allVoters = sum(listOfVotes)
    if len(Link.objects.filter(organization = parliamentary_group, note = 'FB')) > 0:
        FB = Link.objects.filter(organization = parliamentary_group, note = 'FB')[0].url
    else:
        FB = None
    if  len(ContactDetail.objects.filter(organization = parliamentary_group, label = 'Mail')) > 0:
        mail = ContactDetail.objects.filter(organization = parliamentary_group, label = 'Mail')[0].value
    else:
        mail = None
    if len(Link.objects.filter(organization = parliamentary_group, note = 'TW')) > 0:
        twitter = Link.objects.filter(organization = parliamentary_group, note = 'TW')[0].url

    else:
        twitter = None
    data = {
    "HeadOfPG":headOfPG,
    "ViceOfPG":viceOfPG,
    "NumberOfSeats":numberOfSeats,
    "AllVoters":allVoters,
    "Mail":mail,
    "Facebook":FB,
    "Twitter":twitter
    }
    return JsonResponse(data, safe=False)

def getAllPGs(request, date_=None):
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    parliamentary_group = parliamentary_group.filter(Q(founding_date__lte=fdate)|Q(founding_date=None), Q(dissolution_date__gte=fdate)|Q(dissolution_date=None))
    data = {pg.id: {'name': pg.name, 'acronym': pg.acronym, 'id': pg.id, 'is_coalition': True if pg.is_coalition == 1 else False} for pg in parliamentary_group}
    return JsonResponse(data)

def getAllPGsExt(request):
    parliamentary_group = Organization.objects.filter(classification="poslanska skupina")
    data = {pg.id: {'name': pg.name, 'acronym': pg.acronym, 'founded': pg.founding_date, 'disbanded': pg.dissolution_date} for pg in parliamentary_group}
    return JsonResponse(data, safe=False)

def getAllOrganizations(requests):
    org = Organization.objects.all()
    data = {pg.id:{'name':pg.name,'classification':pg.classification, 'acronym': pg.acronym, 'is_coalition': True if pg.is_coalition == 1 else False} for pg in org}
    return JsonResponse(data)


def getAllSpeeches(requests, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().date()
    data = []

    speeches=Speech.objects.filter(start_time__lte=fdate)
    for speech in speeches:
        data.append(model_to_dict(speech, fields=[field.name for field in speech._meta.fields], exclude=[]))

    return JsonResponse(data, safe=False)


def getAllVotes(requests, date_):
    fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()+timedelta(days=1)-timedelta(minutes=1)
    data = []

    votes=Vote.objects.filter(start_time__lte=fdate).order_by("start_time")
    for vote in votes:
        data.append({'id': vote.id,
                     'motion': vote.motion.text,
                     'party': vote.organization.id,
                     'session': vote.session.id,
                     'start_time': vote.start_time,
                     'end_time': vote.end_time,
                     'result': vote.result})

    return JsonResponse(data, safe=False)


def getAllBallots(requests, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    data = [model_to_dict(ballot, fields=['id', 'vote', 'voter', 'option'], exclude=[]) for ballot in Ballot.objects.filter(vote__start_time__lte=fdate)]
    return JsonResponse(data, safe=False)


def getAllPeople(requests):
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    data = []
    pg=''
    person = Person.objects.all()
    for i in person:
        membership = Membership.objects.filter(person = i.id, organization=parliamentary_group)
        for me in membership:
            pg = me.organization.name
        data.append({'id': i.id, 'name':i.name, 'membership':pg, 'classification':i.classification,'family_name':i.family_name,'given_name':i.given_name,'additional_name':i.additional_name,'honorific_prefix':i.honorific_prefix,'honorific_suffix':i.honorific_suffix,'patronymic_name':i.patronymic_name,'sort_name':i.sort_name,'email':i.email,'gender':i.gender,'birth_date':str(i.birth_date),'death_date':str(i.death_date),'summary':i.summary,'biography':i.biography,'image':i.image,'district':'','gov_id':i.gov_id,'gov_picture_url':i.gov_picture_url,'voters':i.voters,'active':i.active})
        pg=None
    return  JsonResponse(data, safe=False)

def motionOfSession(request, id_se):
    data = {}
    tab = []
    allIDs = Session.objects.values('id')
    for i in allIDs:
        tab.append(i['id'])
    if int(id_se) in tab:
        motion = Vote.objects.filter(motion__session__id = id_se)
        if motion:
            data = [{'id':mot.motion.id, 'vote_id': mot.id, 'text':mot.motion.text,'result':mot.result, 'tags': map(smart_str, mot.tags.names())} for mot in motion]
        else:
            #data = "This session has no motion."
            data = []
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse([], safe=False)

def getVotesOfSession(request, id_se):

    votes = Vote.objects.filter(motion__session__id = str(id_se))
    fdate = Session.objects.get(id=str(id_se)).start_time

    memberships = {mem.person.id: {"org_id": mem.organization.id, "org_acronym": mem.organization.acronym} for mem in Membership.objects.filter(Q(end_time__gte=fdate) | Q(end_time=None), Q(start_time__lte=fdate)|Q(start_time=None), organization__classification__in=["poslanska skupina", "nepovezani poslanec"])}
    mems_ids = memberships.keys()
    print memberships
    data = []
    tab = []
    for bal in Ballot.objects.filter(vote__session__id = str(id_se)):
        if bal.voter.id in mems_ids:
            data.append({"mo_id":bal.vote.motion.id,
                     "mp_id":bal.voter.id,
                     "Acronym":memberships[bal.voter.id]["org_acronym"],
                     "option":bal.option,
                     "pg_id":memberships[bal.voter.id]["org_id"]})
        else:
            print "nima membershipa: ", bal.voter.id
    return JsonResponse(data,safe = False)


def getVotesOfMotion(request, motion_id):
    data = []
    for bal in Ballot.objects.filter(vote__id = str(motion_id)):
        mem = Membership.objects.get(Q(end_time__gte=bal.vote.start_time) | Q(end_time=None),Q(start_time__lte=bal.vote.start_time)|Q(start_time=None), person__id=bal.voter.id, organization__classification__in=["poslanska skupina", "nepovezani poslanec"])
        data.append({'mo_id':bal.vote.motion.id,"mp_id":bal.voter.id,"Acronym":mem.organization.acronym, "option":bal.option, "pg_id":mem.organization.id})
    print len(data)
    return JsonResponse(data,safe = False)


def getNumberOfPersonsSessions(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    person = Person.objects.filter(id=person_id)

    if len(person) < 1:
        return HttpResponse('wrong id')

    else:
        person = person[0]
        sessions_with_vote = list(set([ballot.vote.session for ballot in person.ballot_set.filter(vote__start_time__lte=fdate)]))
        sessions_with_speech = list(set([speech.session for speech in person.speech_set.filter(start_time__lte=fdate)]))

        sessions = set(sessions_with_vote + sessions_with_speech)

        result = {
            'sessions_with_vote': len(sessions_with_vote),
            'sessions_with_speech': len(sessions_with_speech),
            'all_sessions': len(sessions)
        }

        return JsonResponse(result, safe=False)

def getNumberOfFormalSpeeches(request, person_id):
    url = 'http://isci.parlameter.si/filter/besedo%20dajem?people=' + person_id

    person = Person.objects.get(id=int(person_id))

    dz = Organization.objects.get(id=95)

    if len(person.memberships.filter(organization=dz).filter(Q(label='podp') | Q(label='p'))) > 0:
        r = requests.get(url).json()
        return HttpResponse(int(r['response']['numFound']))
    else:
        return HttpResponse(0)

def getExtendedSpeechesOfMP(request, person_id):

    speeches_queryset = Speech.objects.filter(speaker__id = person_id)

    speeches = [{'content': speech.content, 'speech_id': speech.id, 'speaker':speech.speaker.id, 'session_name':speech.session.name, 'session_id':speech.session.id,} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)

def getTaggedVotes(request, person_id):

    votes_queryset = Vote.objects.filter(tags__name__in=['Komisija za nadzor javnih financ', 'Kolegij predsednika Državnega zbora', 'Komisija za narodni skupnosti', 'Komisija za odnose s Slovenci v zamejstvu in po svetu', 'Komisija za poslovnik', 'Mandatno-volilna komisija', 'Odbor za delo, družino, socialne zadeve in invalide', 'Odbor za finance in monetarno politiko', 'Odbor za gospodarstvo', 'Odbor za infrastrukturo, okolje in prostor', 'Odbor za izobraževanje, znanost, šport in mladino', 'Odbor za kmetijstvo, gozdarstvo in prehrano', 'Odbor za kulturo', 'Odbor za notranje zadeve, javno upravo in lokalno samoupravo', 'Odbor za obrambo', 'Odbor za pravosodje', 'Odbor za zadeve Evropske unije', 'Odbor za zdravstvo', 'Odbor za zunanjo politiko', 'Preiskovalna komisija o ugotavljanju zlorab v slovenskem bančnem sistemu ter ugotavljanju vzrokov in', 'Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investiciji', 'Ustavna komisija', 'Proceduralna glasovanja', 'Zunanja imenovanja', 'Poslanska vprašanja', 'Komisija za nadzor obveščevalnih in varnostnih služb', 'Preiskovalne komisije'])

    person = Person.objects.filter(id=int(person_id))[0]
    ballots = person.ballot_set.filter(vote__in=votes_queryset)

    votes = [{'name': vote.name, 'motion_id': vote.motion.id, 'session_id': vote.session.id, 'id': vote.id, 'result': vote.result, 'tags': [tag.name for tag in vote.tags.all()]} for vote in votes_queryset]

    ballots_out = [{
        'option': ballot.option,
        'vote': {
            'name': ballot.vote.name,
            'motion_id': ballot.vote.motion.id,
            'session_id': ballot.vote.session.id,
            'id': ballot.vote.id,
            'result': ballot.vote.result,
            'date': ballot.vote.start_time,
            'tags': [tag.name for tag in ballot.vote.tags.all()]
        }} for ballot in ballots]

    return JsonResponse(ballots_out, safe=False)


def getMembersOfPGsRanges(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    tempDate=settings.MANDATE_START_TIME.date()
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    out = {(tempDate+timedelta(days=xday)): {grup: [] for grup in parliamentary_group.values_list("id", flat=True)} for xday in range((fdate-tempDate).days+1)}
    for member in members:
        if not member.start_time and not member.end_time:
            start_time = tempDate
            end_time = fdate
        elif member.start_time and not member.end_time:
            if member.start_time.date() < tempDate:
                start_time = tempDate
            else:
                start_time = member.start_time.date()
            end_time = fdate
        else:
            start_time = member.start_time.date()
            if fdate > member.end_time.date():
                end_time = member.end_time.date()
            else:
                end_time = fdate
        for xday in range((end_time-start_time).days+1):
            out[(start_time+timedelta(days=xday))][member.organization.id].append(member.person.id)

    keys = out.keys()
    keys.sort()
    outList = [{"start_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "end_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "members":out[keys[0]]}]
    for key in keys:
        if out[key]==outList[-1]["members"]:
            outList[-1]["end_date"]=key.strftime(settings.API_DATE_FORMAT)
        else:
            outList.append({"start_date":key.strftime(settings.API_DATE_FORMAT),
                            "end_date":key.strftime(settings.API_DATE_FORMAT),
                            "members":out[key]})


    return JsonResponse(outList, safe=False)


def getMembersOfOrgsRanges(request, org_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    
    organization = Organization.objects.filter(id=org_id)
    members = Membership.objects.filter(organization__in=organization)
    try:
        tempDate=min([mem for mem in members.values_list("start_time", flat=True) if mem]).date()
    except: # if in org isn't members
        tempDate=settings.MANDATE_START_TIME.date()
    out = {(tempDate+timedelta(days=xday)): {grup: [] for grup in organization.values_list("id", flat=True)} for xday in range((fdate-tempDate).days+1)}
    for member in members:
        if not member.start_time and not member.end_time:
            start_time = tempDate
            end_time = fdate
        elif member.start_time and not member.end_time:
            if member.start_time.date() < tempDate:
                start_time = tempDate
            else:
                start_time = member.start_time.date()
            end_time = fdate
        else:
            start_time = member.start_time.date()
            if fdate > member.end_time.date():
                end_time = member.end_time.date()
            else:
                end_time = fdate
        for xday in range((end_time-start_time).days+1):
            out[(start_time+timedelta(days=xday))][member.organization.id].append(member.person.id)

    keys = out.keys()
    keys.sort()
    outList = [{"start_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "end_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "members":out[keys[0]]}]
    for key in keys:
        if out[key]==outList[-1]["members"]:
            outList[-1]["end_date"]=key.strftime(settings.API_DATE_FORMAT)
        else:
            outList.append({"start_date":key.strftime(settings.API_DATE_FORMAT),
                            "end_date":key.strftime(settings.API_DATE_FORMAT),
                            "members":out[key]})


    return JsonResponse(outList, safe=False)


def getMembersOfPGRanges(request, org_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    tempDate=settings.MANDATE_START_TIME.date()
    members = Membership.objects.filter(organization__id=org_id)
    out = {(tempDate+timedelta(days=xday)): {int(org_id): []} for xday in range((fdate-tempDate).days+1)}
    for member in members:
        if not member.start_time and not member.end_time:
            start_time = tempDate
            end_time = fdate
        elif member.start_time and not member.end_time:
            if member.start_time.date() < tempDate:
                start_time = tempDate
            else:
                start_time = member.start_time.date()
            end_time = fdate
        else:
            start_time = member.start_time.date()
            if fdate > member.end_time.date():
                end_time = member.end_time.date()
            else:
                end_time = fdate
        for xday in range((end_time-start_time).days+1):
            out[(start_time+timedelta(days=xday))][member.organization.id].append(member.person.id)

    keys = out.keys()
    keys.sort()
    outList = [{"start_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "end_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "members":out[keys[0]][int(org_id)]}]
    for key in keys:
        if out[key][int(org_id)]==outList[-1]["members"]:
            outList[-1]["end_date"]=key.strftime(settings.API_DATE_FORMAT)
        else:
            outList.append({"start_date":key.strftime(settings.API_DATE_FORMAT),
                            "end_date":key.strftime(settings.API_DATE_FORMAT),
                            "members":out[key][int(org_id)]})


    return JsonResponse(outList, safe=False)


def getMembershipsOfMember(request, person_id, date=None):
    if date:
        fdate = datetime.strptime(date, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    memberships = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), person__id=person_id)

    out_init_dict = {org_type: [] for org_type in set([member.organization.classification for member in memberships])}

    for mem in memberships:
        out_init_dict[mem.organization.classification].append({"org_type": mem.organization.classification, "org_id": mem.organization.id, "name": mem.organization.name})
    return JsonResponse(out_init_dict)
    #return JsonResponse({"org_type": mem.organization.classification, "org_id": mem.organization.id, "name": mem.organization.name} for mem in memberships], safe=False)


def getAllTimeMemberships(request):
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    return JsonResponse([{"start_time": member.start_time,
                          "end_time": member.end_time,
                          "id": member.person.id,} for member in members], safe=False)


def getAllTimeMPs(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().today()
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), organization__in=parliamentary_group)
    return JsonResponse([{'id': i.person.id, 'name':i.person.name,'membership':i.organization.name, 'acronym':i.organization.acronym,'classification':i.person.classification,'family_name':i.person.family_name,'given_name':i.person.given_name,'additional_name':i.additional_name,'honorific_prefix':i.honorific_prefix,'honorific_suffix':i.honorific_suffix,'patronymic_name':i.patronymic_name,'sort_name':i.sort_name,'email':i.email,'gender':i.gender,'birth_date':str(i.birth_date),'death_date':str(i.death_date),'summary':i.summary,'biography':i.biography,'image':i.image,'district':'','gov_url':i.gov_url.url,'gov_id':i.gov_id,'gov_picture_url':i.gov_picture_url,'voters':i.voters,'active':i.active,'party_id':i[0].organization.id} for i in members], safe=False)


def getOrganizatonByClassification(request):
    workingBodies = Organization.objects.filter(classification__in=["odbor", "komisija", "preiskovalna komisija"])
    parliamentaryGroups = Organization.objects.filter(classification__in=["poslanska skupina", "nepovezani poslanec"])
    council = Organization.objects.filter(classification="kolegij")

    return JsonResponse({"working_bodies": [{"id": wb.id, "name": wb.name} for wb in workingBodies],
                         "parliamentary_groups": [{"id": pg.id, "name": pg.name} for pg in parliamentaryGroups],
                         "council": [{"id": c.id, "name": c.name} for c in council]})


def getOrganizationRolesAndMembers(request, org_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate=datetime.now().today()
    org = Organization.objects.filter(id=org_id)
    out = {}
    trans_map = {"debug": "debug","predsednik": "president", "predsednica": "president", smart_str("član"): "members", smart_str("namestnica člana"): "viceMember", smart_str("namestnik člana"): "viceMember", smart_str("članica"): "members", "podpredsednica": "vice_president", "podpredsednik": "vice_president"}
    if org:
        out = {"debug": [],"members":[], "president":[], "vice_president":[], "viceMember":[]}
        out["name"]=org[0].name
        memberships = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), organization_id=org_id)
        #out = {trans_map[mem_type.encode("utf-8")]: [] for mem_type in set(list(memberships.values_list("role", flat=True)))}
        for member in memberships:
            post = member.memberships.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None))
            if post:
                out[trans_map[smart_str(post[0].role)]].append(member.person.id)
            else:
                out[trans_map[smart_str("debug")]].append(member.person.id)
        out["members"] += out["debug"]
    return JsonResponse(out)


def getTags(request):
    out = [{"name": tag.name, "id": tag.id} for tag in Tag.objects.all().exclude(id__in=[1,2,3,4,5,8,9])]
    return JsonResponse(out, safe=False)


def getDistricts(request):
    out = [{"id": area.id, "name": area.name} for area in Area.objects.filter(calssification="okraj")]
    return JsonResponse(out, safe=False)


def getSpeechData(request, speech_id):
    speech = Speech.objects.filter(pk=speech_id)

    if len(speech) > 0:
        speech = speech[0]

        output = {
            'id': int(speech_id),
            'date': speech.session.start_time.date(),
            'speaker_id': speech.speaker.id,
            'session_id': speech.session.id,
            'session_name': speech.session.name
        }

        return JsonResponse(output, safe=False)

    return HttpResponse(-1)

def getResultOfMotion(request, motion_id):
    output = {"result":Motion.objects.get(id=motion_id).result}
    return JsonResponse(output, safe=False)

def getPersonData(request, person_id):
    person = Person.objects.filter(id=person_id)
    if person:
        obj = {'name': person[0].name,          
               'gender':person[0].gender if person[0].gender else 'unknown',
               'gov_id':person[0].gov_id,
               }
    else:
        obj = {}
    return JsonResponse(obj)


def isSpeechOnDay(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate=datetime.now()
    print fdate
    print fdate+timedelta(hours=23, minutes=59)
    speech = Speech.objects.filter(start_time__gte=fdate, start_time__lte=(fdate+timedelta(hours=23, minutes=59)))
    return JsonResponse({"isSpeech": True if speech else False})


def isVoteOnDay(request, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate=datetime.now()
    print fdate
    print fdate+timedelta(hours=23, minutes=59)
    votes = Vote.objects.filter(start_time__gte=fdate, start_time__lte=(fdate+timedelta(hours=23, minutes=59)))
    return JsonResponse({"isVote": True if votes else False})


#return speech ids of MPs
def getSpeechesIDs(request, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate=datetime.now()
    fdate = fdate.replace(hour=23, minute=59)
    speaker = get_object_or_404(Person, id=person_id)
    speeches_ids = list(Speech.objects.filter(speaker=speaker, start_time__lte=fdate).values_list("id", flat=True))

    return JsonResponse(speeches_ids, safe=False)

#return speech ids
def getPGsSpeechesIDs(request, org_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate=datetime.now()
    fdate = fdate.replace(hour=23, minute=59)
    org = get_object_or_404(Organization, id=org_id)
    ranges = json.loads(getMembersOfPGRanges(request, org_id, date_).content)

    speeches_ids = []

    for ran in ranges:
        start = datetime.strptime(ran["start_date"], settings.API_DATE_FORMAT)
        start = start.replace(hour=23, minute=59)
        end = datetime.strptime(ran["end_date"], settings.API_DATE_FORMAT)
        end = end.replace(hour=23, minute=59)
        for member in ran["members"]:
            speeches_ids += list(Speech.objects.filter(speaker__id=member, start_time__lte=end, start_time__gte=start).values_list("id", flat=True))

    return JsonResponse(speeches_ids, safe=False)


def getMembersWithFuction(request):
    fdate = datetime.today()
    data = []
    dz = Organization.objects.filter(id=95)
    members = Membership.objects.filter(Q(start_time__lte=fdate)|Q(start_time=None), Q(end_time__gte=fdate)|Q(end_time=None), organization__in=dz)
    for member in members:
        for post in member.memberships.all():
            if post.role in ["predsednik", "podpredsednik"]:
                data.append(member.person.id)

    return JsonResponse({"members_with_function": data}, safe=False)

def getDocumentOfMotion(request, motion_id):
    if Link.objects.filter(motion=motion_id):
        link = str(Link.objects.filter(motion=motion_id)[0]).split('/')
        return JsonResponse({"link":str('https://cdn.parlameter.si/v1/dokumenti/'+link[4])}, safe=False)
    else:
        return JsonResponse({"link":None}, safe=False)
    