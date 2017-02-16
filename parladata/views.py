# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
from parladata.models import *
from django.db.models import Q, Count
from django.forms.models import model_to_dict
import json
from utils import *
import requests
from raven.contrib.django.raven_compat.models import client
from collections import OrderedDict
from django.conf import settings
from django.utils.encoding import smart_str
from taggit.models import Tag
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.expressions import DateTime

DZ_ID = 95
PS_NP = ['poslanska skupina', 'nepovezani poslanec']
PS = 'poslanska skupina'


def getActivity(request, person_id):
    """Return all ballots and speaches agregated by date
       id: id of person
    """

    def appendBallot(data, b):
        tempBallot = dict()
        tempBallot['type'] = 'ballot'
        tempBallot['date'] = str(b.vote.start_time.date())
        tempBallot['option'] = b.option
        tempBallot['result'] = b.vote.result
        tempBallot['vote_id'] = b.vote.id
        tempBallot['vote_name'] = b.vote.name
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
        ballots = Ballot.objects.filter(voter=person)
        speeches_queryset = Speech.getValidSpeeches(fdate)
        speeches = speeches_queryset.filter(speaker=person)

        for b in ballots.order_by('vote__start_time'):
            appendBallot(data, b)
        for s in speeches.order_by('start_time'):
            appendSpeech(data, s)
    data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))

    data_list = [data[x] for x in data]
    return JsonResponse(data_list, safe=False)


def getMPs(request, date_=None):
    """
    * @api {get} getMPs/{?date} List of MPs active today
    * @apiName getMPs
    * @apiGroup MPs
    * @apiDescription This function returns all MPs active on a given day.
      It returns an array of MP objects.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} mp MP object.
    * @apiSuccess {String} mp.gov_id MP's "government id". The ID this
      particular MP is given on http://www.dz-rs.si
    * @apiSuccess {String} mp.hovorific_suffix MP's honorific suffix, such as "PhD".
    * @apiSuccess {String} mp.image URL to MPs image on http://www.dz-rs.si.
    * @apiSuccess {String} mp.patronymic_name MP's patronymic name if applicable.
      If not returns empty string.
    * @apiSuccess {String} mp.sort_name MP's sorting name if applicable.
      If not returns empty string.
    * @apiSuccess {Integer} mp.id MP's Parladata id.
    * @apiSuccess {String} mp.biography MP's biography if applicable.
      If not returns empty string.
    * @apiSuccess {String} mp.classification MP's classification if applicable.
      If not returns empty string. Sometimes used for internal sorting purposes.
    * @apiSuccess {String[]} mp.district Name of the district (or districts) the MP was elected in.
    * @apiSuccess {String} mp.additional_name MP's additional name if applicable.
      If not returns empty string.
    * @apiSuccess {Integer} mp.voters The number of voters the MP was elected with.
    * @apiSuccess {String} mp.honorific_prefix MP's honorific prefix name if applicable.
      If not returns empty string.
    * @apiSuccess {String} mp.given_name MP's given name.
    * @apiSuccess {String} mp.email MP's email.
    * @apiSuccess {String} mp.acronym MP's party acronym.
    * @apiSuccess {String} mp.membership MP's current party.
    * @apiSuccess {Integer} mp.party_id MP's current party Parladata id.
    * @apiSuccess {Boolean} mp.active MP's active state.
    * @apiSuccess {String} mp.family_name MP's family name.
    * @apiSuccess {String} mp.name MP's full/display name.
    * @apiSuccess {String} mp.gov_picture_url URL to MPs image on http://www.dz-rs.si.
    * @apiSuccess {String} mp.summary MP's summary if applicable. If not returns empty string.
    * @apiSuccess {String} mp.birth_date MP's date of birth. Returns time as well, so that all
      objects are datetime, but the time can be ignored.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMPs
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMPs/21.12.2016

    * @apiSuccessExample {json} Example response:
    [{
        "gov_id": "P280",
        "honorific_suffix": "",
        "image": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P280",
        "patronymic_name": "",
        "sort_name": "",
        "id": 69,
        "biography": "",
        "classification": "",
        "district": ["Maribor VII"],
        "additional_name": "",
        "voters": 1245,
        "honorific_prefix": "",
        "given_name": "Uro\u0161",
        "email": "uros.prikl@dz-rs.si",
        "acronym": "DeSUS",
        "membership": "PS Demokratska Stranka Upokojencev Slovenije",
        "party_id": 3,
        "active": true,
        "family_name": "Prikl",
        "name": "Uro\u0161 Prikl",
        "gov_picture_url": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P280",
        "gender": "male",
        "death_date": "None",
        "gov_url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/PoslankeInPoslanci/poslanec?idOseba=P280",
        "summary": "",
        "birth_date": "1972-09-18 01:00:00"
    }, {
        "gov_id": "P289",
        "honorific_suffix": "",
        "image": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P289",
        "patronymic_name": "",
        "sort_name": "",
        "id": 80,
        "biography": "",
        "classification": "",
        "district": ["Ljubljana - center"],
        "additional_name": "",
        "voters": 1421,
        "honorific_prefix": "",
        "given_name": "Violeta",
        "email": "violeta.tomic@dz-rs.si",
        "acronym": "ZL",
        "membership": "PS Zdru\u017eena Levica",
        "party_id": 8,
        "active": true,
        "family_name": "Tomi\u0107",
        "name": "Violeta Tomi\u0107",
        "gov_picture_url": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P289",
        "gender": "female",
        "death_date": "None",
        "gov_url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/PoslankeInPoslanci/poslanec?idOseba=P289",
        "summary": "",
        "birth_date": "1963-01-21 01:00:00"
    }]
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().today()
    data = []

    for i in getMPObjects(fdate):
        districts = ''

        if i.districts:
            districts = i.districts.all().values_list("name", flat=True)
            districts = [smart_str(dist) for dist in districts]
            if not districts:
                districts = None
        else:
            districts = None
        membership = i.memberships.all().filter(Q(start_time__lte=fdate) |
                                                Q(start_time=None),
                                                Q(end_time__gte=fdate) |
                                                Q(end_time=None))
        membership = membership.filter(organization__classification__in=PS_NP)
        ps = membership[0] if membership else None

        data.append({'id': i.id,
                     'name': i.name,
                     'membership': ps.organization.name if ps else None,
                     'acronym': ps.organization.acronym if ps else None,
                     'classification': i.classification,
                     'family_name': i.family_name,
                     'given_name': i.given_name,
                     'additional_name': i.additional_name,
                     'honorific_prefix': i.honorific_prefix,
                     'honorific_suffix': i.honorific_suffix,
                     'patronymic_name': i.patronymic_name,
                     'sort_name': i.sort_name,
                     'email': i.email,
                     'gender': i.gender,
                     'birth_date': str(i.birth_date),
                     'death_date': str(i.death_date),
                     'summary': i.summary,
                     'biography': i.biography,
                     'image': i.image,
                     'district': districts,
                     'gov_url': i.gov_url.url,
                     'gov_id': i.gov_id,
                     'gov_picture_url': i.gov_picture_url,
                     'voters': i.voters,
                     'active': i.active,
                     'party_id': ps.organization.id if ps else None})

    return JsonResponse(data, safe=False)


def getMPStatic(request, person_id, date_=None):
    """
    * @api {get} getMPStatic/{id}/{?date} MP's static info
    * @apiName getMPStatic
    * @apiGroup MPs
    * @apiDescription This function returns an object with all 
      "static" data belonging to an MP. By static we mean that it
      is entered and maintained by hand and rarely, if ever, changes.
    * @apiParam {Integer} id MPs Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {String} gov_id MP's "government id". The ID this
      particular MP is given on http://www.dz-rs.si
    * @apiSuccess {Integer} voters The number of voters the MP was elected with.
    * @apiSuccess {String} acronym MP's party acronym.
    * @apiSuccess {Integer} mandates Total number of mandates this MP has held,
      including (if applicable) their current one.
    * @apiSuccess {Integer} party_id MP's current party Parladata id.
    * @apiSuccess {Object[]} groups Working bodies the MP is a member of.
    * @apiSuccess {String} name Name of the working body.
    * @apiSuccess {Integer} id Working body's Parladata id.
    * @apiSuccess {String} education MPs education.
    * @apiSuccess {Object[]} working_bodies_functions Functions the MP holds in
      working bodies.
    * @apiSuccess {String} working_bodies_functions.role MP's role in this working body.
    * @apiSuccess {Integer} working_bodies_functions.id Working body's id.
    * @apiSuccess {String} previous_occupation MP's previous occupation. Previous
      in this case means before their current term, not before their political career.
    * @apiSuccess {String} name MP's full/display name.
    * @apiSuccess {Integer[]} district Parladata id of district (or districts) the MP was elected in.
    * @apiSuccess {String} gender MP's gender.
    * @apiSuccess {Integer} age MP's age.
    * @apiSuccess {Object} social MP's social profiles.
    * @apiSuccess {String} social.twitter MP's Twitter profile. Returns false (as type boolean)
      if no profile is on record.
    * @apiSuccess {String} social.facebook MP's Facebook profile. Returns false (as boolean)
      if no profile is on record.
    * @apiSuccess {String} social.linkedin MP's LinkedIn profile. Returns false (as boolean)
      if no profile is on record.
    * @apiSuccess {String} party Full name of MP's party.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMPStatic/12
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMPStatic/12/21.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "gov_id": "P244",
        "voters": 2043,
        "acronym": "SDS",
        "mandates": 1,
        "party_id": 5,
        "groups": [{
            "name": "Komisija za poslovnik",
            "id": 14
        }, {
            "name": "Odbor za notranje zadeve, javno upravo in lokalno samoupravo",
            "id": 23
        }, {
            "name": "Odbor za zdravstvo",
            "id": 27
        }, {
            "name": "Odbor za finance in monetarno politiko",
            "id": 17
        }, {
            "name": "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino",
            "id": 20
        }, {
            "name": "Preiskovalna komisija o ugotavljanju zlorab v slovenskem zdravstvenem sistemu na podro\u010dju prodaje in nakupa \u017eilnih opornic",
            "id": 106
        }],
        "education": "specialistka javne uprave",
        "working_bodies_functions": [{
            "role": "vice_president",
            "org_id": 27
        }],
        "previous_occupation": "direktorica ob\u010dinske uprave ",
        "name": "Nada Brinov\u0161ek",
        "district": [35],
        "gender": "f",
        "age": 55,
        "social": {
            "twitter": "https://twitter.com/nadabrinovsek",
            "facebook": "https://www.facebook.com/nada.brinovsek",
            "linkedin": false
        },
        "party": "PS Slovenska Demokratska Stranka"
    }
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = dict()
    for member in getMPObjects(fdate):
        memberships = member.memberships.filter(Q(start_time__lte=fdate) |
                                                Q(start_time=None),
                                                Q(end_time__gte=fdate) |
                                                Q(end_time=None))

        if str(member.id) == str(person_id):
            groups = [{'name': membership.organization.name,
                       'id': membership.organization.id,
                       'acronym': membership.organization.acronym}
                      for membership
                      in memberships
                      if membership.organization.classification in PS_NP]
            if not groups:
                return JsonResponse({})

            non_party_groups = [{'name': membership.organization.name,
                                 'id': membership.organization.id}
                                for membership
                                in memberships
                                if membership.organization.classification not in PS_NP]

            for group in non_party_groups:
                groups.append(group)

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


def getSessions(request, date_=None):
    """Returns all Sessions from beginning of mandate."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    sessions = Session.objects.filter(start_time__lte=fdate).order_by('-start_time')

    for i in sessions:
        organizations = i.organizations.all().values_list('id', flat=True)
        data.append({'mandate': i.mandate,
                     'name': i.name,
                     'gov_id': i.gov_id,
                     'start_time': i.start_time,
                     'end_time': i.end_time,
                     'organizations_id': map(str, organizations),
                     'classification': i.classification,
                     'id': i.id,
                     'is_in_review': i.in_review,
                     }
                    )

    return JsonResponse(data, safe=False)


def getSessionsOfOrg(request, org_id, date_=None):
    """Returns all Sesisons of specific organization."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    sessions = Session.objects.filter(organization__id=org_id,
                                      start_time__lte=fdate)
    for i in sessions.order_by('-start_time'):
        data.append({'mandate': i.mandate,
                     'name': i.name,
                     'gov_id': i.gov_id,
                     'start_time': i.start_time,
                     'end_time': i.end_time,
                     'classification': i.classification,
                     'id': i.id
                     }
                    )

    return JsonResponse(data, safe=False)


def getVotes(request, date_=None):
    """Returns votes of MPs."""

    return JsonResponse(getVotesDict(date_))


def getSpeeches(request, person_id, date_=None):
    """Returns speechs of MP."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    speaker_list = Person.objects.filter(id=person_id)
    if len(speaker_list) > 0:
        speaker = speaker_list[0]

    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker=speaker,
                                                 start_time__lte=fdate)

    speeches = [{'content': speech.content,
                 'speech_id': speech.id} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


def getSpeechesInRange(request, person_id, date_from, date_to):
    """Returns speechs of MP in range(from specific date to specific date)."""

    fdate = datetime.strptime(date_from, settings.API_DATE_FORMAT).date()
    tdate = datetime.strptime(date_to, settings.API_DATE_FORMAT).date()

    speaker = get_object_or_404(Person, id=person_id)
    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker=speaker,
                                                 start_time__lte=tdate,
                                                 start_time__gte=fdate)

    speeches = [{'content': speech.content,
                 'speech_id': speech.id} for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


def getMembersOfPGs(request):
    """Returns list of member's id for each PG.
    PG = Parlamentary group
    """

    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(Q(end_time=None) |
                                        Q(end_time__gt=datetime.now()),
                                        organization__in=parliamentary_group
                                        )
    data = {pg.id: [member.person.id
                    for member
                    in members.filter(organization=pg)
                    ] for pg in parliamentary_group}

    return JsonResponse(data)


def getMembersOfPGsOnDate(request, date_=None):
    """Returns list of member's id for each PG, on specific date."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        organization__in=parliamentary_group
                                        )
    data = {pg.id: [member.person.id for member in members.filter(organization=pg)] for pg in parliamentary_group}

    return JsonResponse(data)


def getCoalitionPGs(request):
    """Returns coalitions PGs."""

    coalition = Organization.objects.filter(classification=PS,
                                            is_coalition="1").values_list("id", flat=True)
    oppo = Organization.objects.filter(classification=PS)
    oppo = oppo.exclude(is_coalition="1").values_list("id", flat=True)

    return JsonResponse({'coalition': list(coalition), 'opposition': list(oppo)})


def getNumberOfMPAttendedSessions(request, person_id):
    """
    TODO DELETE!!!
    Returns number of MP attended sessions.
    """
    

    data = {}
    allBallots = Ballot.objects.filter(option='za')
    for i in getMPObjects():
        data[i.id] = len(list(set(allBallots.filter(voter=i.id).values_list('vote__session', flat=True))))

    return JsonResponse(data[int(person_id)], safe=False)


def getNumberOfAllMPAttendedSessions(request, date_):
    """
    * @api {get} getNumberOfAllMPAttendedSessions/{date}/ Percentage of attended sessions and votes
    * @apiName getNumberOfAllMPAttendedSessions
    * @apiGroup MPs
    * @apiDescription This function returns all MPs and the percentage of sessions
      and votes they attended up until a given date.
    * @apiParam {date} date Date up until which attendance percentage should be calculated.

    * @apiSuccess {Object} votes MPs' vote attendance.
    * @apiSuccess {Float} :id MP's attendance. Key is MP's Parladata id.
    * @apiSuccess {Object} sessions MPs' vote attendance.
    * @apiSuccess {Float} :id MP's attendance. Key is MP's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getNumberOfAllMPAttendedSessions/5.2.2017
    
    * @apiSuccessExample {json} Example response:
    {
        "votes": {
            "2": 75.10416666666667,
            "3": 99.6875,
            "4": 55.00000000000001,
            "7": 64.0625,
            "8": 93.64583333333333,
            "9": 45.520833333333336,
            "10": 71.77083333333333,
        },
        "sessions": {
            "2": 87.17948717948718,
            "3": 100.0,
            "4": 64.1025641025641,
            "7": 97.43589743589743,
            "8": 97.43589743589743,
            "9": 71.7948717948718,
            "10": 79.48717948717949,
        }
    }
    """

    fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date() + timedelta(days=1) - timedelta(minutes=1)
    data = {"sessions": {}, "votes": {}}
    for member in getMPObjects(fdate):
        # list of all sessions of MP
        allOfHimS = list(set(Ballot.objects.filter(voter__id=member.id,
                                                   vote__start_time__lte=fdate).values_list("vote__session", flat=True)))
        # list of all session that the opiton of Ballot was: kvorum, proti, za
        votesOnS = list(set(Ballot.objects.filter(Q(option="kvorum") |
                                                  Q(option="proti") |
                                                  Q(option="za"),
                                                  voter__id=member.id,
                                                  vote__start_time__lte=fdate).values_list("vote__session", flat=True)))
        # list of all votes of MP
        allOfHimV = list(set(Ballot.objects.filter(voter__id=member.id,
                                                   vote__start_time__lte=fdate).values_list("vote", flat=True)))
        # list of all votes that the opiton of ballot was: kvorum, proti, za
        votesOnV = list(set(Ballot.objects.filter(Q(option="kvorum") |
                                                  Q(option="proti") |
                                                  Q(option="za"),
                                                  voter__id=member.id,
                                                  vote__start_time__lte=fdate).values_list("vote", flat=True)))
        try:
            data["sessions"][member.id] = float(len(votesOnS)) / float(len(allOfHimS)) * 100
            data["votes"][member.id] = float(len(votesOnV)) / float(len(allOfHimV)) * 100
        except:
            print member.id, " has no votes in this day"

    return JsonResponse(data)


def getSpeechesOfMP(request, person_id, date_=None):
    """
    * @api {get} getSpeechesOfMP/{id}/{?date} MP's speeches
    * @apiName getSpeechesOfMP
    * @apiGroup MPs
    * @apiDescription This function returns an array of strings, each string
      being the full contents of one of your chosen MP's speeches. Optionally it returns speeches
      up until the optionally passed date.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {String[]} / An array of all speeches as strings.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSpeechesOfMP/12
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getSpeechesOfMP/12/21.12.2016

    * @apiSuccessExample {json} Example response:
    [
        "Hvala za besedo. Lep pozdrav vsem. Predsednik, upam, da boste dovolili, da pa\u010d nekaj na splo\u0161no o tem Zakonu.\nPoglejte, ko smo se 10. novembra tule pogovarjali in smo nekako se strinjali, da se ta Zakon umakne z dnevnega reda, pa\u010d zaradi tega, ker je koalicija menila, da je bilo pomanjkanje \u010dasa za pripravo amandmajev, ki jih je bilo kar veliko. In s tem se strinjam, ker spet imamo primer, da je tri \u010detrt \u010dlenov tega Zakona amandmiranih. Ampak poglejte, \u0161e danes nimamo enega takega primernega \u010distopisa, \u010de smo poslu\u0161ali gospo Kurent iz Zakonodajno-pravne slu\u017ebe, pravi, da je \u0161e Zakon vedno nepopoln, nejasen, nepregleden, da si nekatere dolo\u010dbe nasprotujejo. \nPoslu\u0161ali smo tudi oziroma tudi predstavnik Zdravni\u0161ke zbornice je podal svoje pomisleke in predstavil njihovo sodelovanje pri pripravi tega Zakona in pa tudi, zdajle smo kolega poslu\u0161ali, da \u0161e je nekaj odprtih dilem v zvezi s tem Zakonom.\nAmpak, kar pa ho\u010dem re\u010di, poglejte, nobeden pa ni omenil tega, Evropska komisija nas je namre\u010d 30. 9. opozorila, da je potrebno prenesti to Direktivo oziroma spremeniti ta Zakon od 30. 11. In v nasprotnem primeru, \u010de se to ne zgodi, da bodo lahko tudi finan\u010dne posledice. Jaz bi tele predstavnice Ministrstva vpra\u0161ala, kdo bo v tem primeru nosil finan\u010dne posledice. Ni zanemarljivo, pi\u0161e, sam pi\u0161ete tule v va\u0161emu pisanju k tej to\u010dki, da je to lahko od 710 evrov do 14.000 evrov dnevno. To bi res rada odgovor na to vpra\u0161anje.\nIn pa \u0161e eno vpra\u0161anje imam. Mislim, da je bila to zadnja seja na\u0161ega Odbora, ko smo se pogovarjali o reviziji oziroma prenovi srednje\u0161olskih programov oziroma srednje\u0161olskega programa zdravstvena nega in tudi tu se je omenjala ta Direktiva 2013/55/EU, tak ko je tu, in tu bi tudi rada, \u010de mi lahko res jasno odgovorite, ali se to nana\u0161a tudi kaj na te srednje medicinske sestre oziroma karkoli. Hvala lepa.",
        "Hvala za besedo, predsedujo\u010di. Spo\u0161tovani navzo\u010di!\n\u017divimo v dr\u017eavi, kjer nam vlada tak\u0161na vlada, ki ne spo\u0161tuje odlo\u010db Ustavnega sodi\u0161\u010da, ne spo\u0161tuje odlo\u010db sodi\u0161\u010d, kjer ministrstva ne spo\u0161tujejo zakonov in kjer se ne kaznuje tistih, ki naredijo oziroma povzro\u010dijo neko \u0161kodo, ampak tiste, ki na to opozarjajo.\nPa se bom ustavila le na primeru, kjer se zavestno ne upo\u0161teva odlo\u010dbe Ustavnega sodi\u0161\u010da, kar s to interpelacijo o\u010ditamo tudi ministrici za izobra\u017eevanje, znanost in \u0161port dr. Maji Makovec Bren\u010di\u010d. To, kar ji o\u010ditamo mi, ji o\u010dita tudi prej\u0161nji predsednik Ustavnega sodi\u0161\u010da Miroslav Mozeti\u010d, ki je ob predstavitvi Poro\u010dila o delu Ustavnega sodi\u0161\u010da za leto 2015 opozoril, da politika v zadnjih dveh letih odlaga izvr\u0161itev odlo\u010db Ustavnega sodi\u0161\u010da, ker se z njimi ne strinja. Opozoril je \u0161e, da je to z vidika pravne dr\u017eave zelo problemati\u010dno, zlasti \u010de je neizvr\u0161itev pogojena politi\u010dno in ideolo\u0161ko. Med odlo\u010dbami Ustavnega sodi\u0161\u010da je posebej omenil \u0161e primer, da \u0161e vedno ni izvr\u0161ena odlo\u010dba o financiranju zasebnih osnovnih \u0161ol. \nKonec leto\u0161njega leta bo torej minilo \u017ee kar dve leti, odkar je Ustavno sodi\u0161\u010de Republike Slovenije na pobudo star\u0161ev \u0161oloobveznih otrok, ki obiskujejo zasebno osnovno \u0161olo, v svojem postopku za oceno ustavnosti 4. decembra 2014 ugotovilo, da je prvi stavek drugega odstavka 86. \u010dlena Zakona o organizaciji in financiranju vzgoje in izobra\u017eevanja, v delu, ki se nana\u0161a na javno veljavne programe osnovno\u0161olskega izobra\u017eevanja, v neskladju z Ustavo Republike Slovenije. Zakaj protiustavnost zakona? Pobudniki, ki so vlo\u017eili zahtevo za oceno ustavnosti na Ustavno sodi\u0161\u010de, so namre\u010d izpodbijali ta prvi stavek drugega odstavka 86. \u010dlena tega zakona, ki zasebnim \u0161olam, ki izvajajo javno veljavne izobra\u017eevalne programe, za izvedbo programa zagotavlja le 85 % sredstev, ki jih dr\u017eava zagotavlja za izvajanje teh programov. Ustavno sodi\u0161\u010de je torej ugotovilo, da je to diskriminatorno do otrok v zasebnih \u0161olah. Star\u0161i otrok, ki obiskujejo zasebne osnovne \u0161ole, morajo namre\u010d pla\u010devati 15 % za program, kar znese okoli 60 evrov mese\u010dno. Tega zneska, ki ga pla\u010dujejo star\u0161i, glede na odlo\u010ditev Ustavnega sodi\u0161\u010da v letu 2014, od januarja letos ne bi smeli ve\u010d pla\u010devati. Poudarjam, da od januarja letos ne bi smeli ve\u010d pla\u010devati. Ministrica pa v odgovoru na na\u0161o interpelacijo navaja, da je odlo\u010ditev star\u0161ev za vpis otrok v zasebno \u0161olo njihova lastna odlo\u010ditev in da so bili star\u0161i ob vpisu s pogoji financiranja seznanjeni. Spo\u0161tovana ministrica, to ni res. To ne dr\u017ei. Star\u0161i so glede na odlo\u010ditev Ustavnega sodi\u0161\u010da iz leta 2015 verjeli, da se bo spremenila zakonodaja in posledi\u010dno tudi na\u010din financiranja. Verjeli so, da \u017eivijo v neki pravni dr\u017eavi, ampak so se \u017eal zmotili. \nPolo\u017eaj \u0161oloobveznih u\u010dencev v zasebnih \u0161olah je primerljiv s polo\u017eajem \u0161oloobveznih u\u010dencev v javnih \u0161olah. Zato je neenako zagotavljanje javnih sredstev kr\u0161itev na\u010dela enakosti pred zakonom, to je ugotovilo Ustavno sodi\u0161\u010de. \"Osnovno\u0161olsko izobra\u017eevanje je obvezno in se financira iz javnih sredstev, ne glede na to, ali ga izvaja javnopravni ali zasebnopravni subjekt,\" je \u0161e zapisalo Ustavno sodi\u0161\u010de v tej svoji odlo\u010dbi. Da je zadeva \u0161e bolj bizarna, so zasebne \u0161ole, ki so bile ustanovljene pred letom 1996, financirane v vi\u0161ini 100 %, zasebne \u0161ole, ustanovljene po letu 1996, pa zgolj v vi\u0161ini 85 %. Statisti\u010dni podatki ka\u017eejo izrazito prevlado javnih osnovnih \u0161ol. Iz podatkov Eurostata izhaja, da je bilo v Republiki Sloveniji v letu 2011 kar 98,4 % vseh u\u010dencev osnovnih in srednjih \u0161ol, ki so obiskovali javne \u0161ole, evropsko povpre\u010dje je 82 %. 0,9 % sofinancirane zasebne \u0161ole, evropsko povpre\u010dje je tu 10,2 %. In le 0,7 % u\u010dencev je obiskovalo neodvisne zasebne \u0161ole, evropsko povpre\u010dje pa je tu 2,9 %. Trditi, da bo financiranje programov zasebnih osnovnih \u0161ol v \u010demerkoli ogrozilo javne, je torej, milo re\u010deno, sme\u0161no. \nFinanciranje osnovno\u0161olskega izobra\u017eevanja iz javnih sredstev pomeni, da mora to financiranje zagotavljati organizacija ustrezne mre\u017ee osnovnih \u0161ol in delovanje osnovno\u0161olskega izobra\u017eevanja. Vsebina obveznega javno veljavnega programa osnovno\u0161olskega izobra\u017eevanja, ki se financira iz javnih sredstev, je namre\u010d enotno dolo\u010dena za vse izvajalce osnovno\u0161olskega izobra\u017eevanja. To izhaja iz zasledovanja enakih ciljev vzgoje in izobra\u017eevanja, enakovrednega izobrazbenega standarda, enakih pogojev za strokovne delavce, prostor, opremo, enako uporabo u\u010dbenikov za obvezne predmete in nenazadnje za enako omejitev pla\u010d. Vsebinske razlike v na\u010delih, po katerih delujejo zasebne oziroma javne \u0161ole, se poka\u017eejo pa \u0161ele v raz\u0161irjenih izobra\u017eevalnih programih, ki pa se ne financirajo iz javnih sredstev. Treba je lo\u010devati razli\u010dne segmente financiranja, se pravi izvajanje programov, teko\u010de stro\u0161ke in investicije. Skrajni \u010das je \u017ee, da si priznamo, da so za dr\u017eavo zasebne \u0161ole precej cenej\u0161e kot javne \u0161ole. Dr\u017eavi v tem primeru namre\u010d ni treba skrbeti za vse teko\u010de stro\u0161ke in investicije, ki so v tem primeru na ple\u010dih zasebnika. \nNaj \u0161e enkrat poudarim, da pobudniki na Ustavno sodi\u0161\u010de niso vlo\u017eili zahteve za presojo drugega odstavka 86. \u010dlena, po katerem zasebnim \u0161olam ne pripadajo sredstva za nalo\u017ebe, za investicijsko vzdr\u017eevanje in opremo, ampak so vlo\u017eili zahtevo za izvajanje programov. Ustava namre\u010d dolo\u010da, da se javno financira obvezen minimum osnovne izobrazbe, ki je enotno dolo\u010dena po vsebini, kar pa ne zajema dodatnih vsebin, ki so odvisne od vrednostnih usmeritev posameznih izvajalcev osnovno\u0161olskega izobra\u017eevanja. \nV svojem odgovoru na interpelacijo ministrica navaja, da drugi odstavek 57. \u010dlena Ustave dolo\u010da, da je osnovno\u0161olsko izobra\u017eevanje obvezno in da se financira iz javnih sredstev. To dr\u017ei, spo\u0161tovana ministrica, in s tem se popolnoma strinjam. Glede na navedeno naj bi bili tudi u\u010denci, ki obiskujejo zasebne \u0161ole, in pa njihove dru\u017eine dele\u017eni tudi enakih finan\u010dnih koristi, ki so na voljo u\u010dencem javnih \u0161ol in pa tudi njihovim dru\u017einam. Ampak ministrica, zakaj potem ne povle\u010dete poteze in spremenite zakona v skladu z odlo\u010dbo Ustavnega sodi\u0161\u010da? Vi po na\u0161i oceni ne ukrenete ni\u010desar in samo \u010dakate. \u010cakate tako, kot \u010dakajo na\u0161i bolniki v vrstah v na\u0161em zdravstvenem sistemu, \u017eal.\nNaloga ministrstva bi morala biti prvenstveno usmerjena v kvaliteto \u0161ol. Zdrava konkurenca lahko namre\u010d rodi samo ve\u010djo kvaliteto, in to na obeh straneh. Ja, prav imate, ministrica, ko v odgovoru na interpelacijo navajate, da mora biti na\u0161 izobra\u017eevalni sistem dostopen, kakovosten in pravi\u010den. Prav imate tudi v svojih navedbah, da so zasebne \u0161ole s svojimi rezultati dokazale, da svoje delo opravljajo kakovostno. Ampak zakaj potem navajate, da je potrebna jasnej\u0161a ureditev v primerih nastajanja novih zasebnih \u0161ol? Zakaj jasnej\u0161a? Kaj tukaj ni jasno? Rezultati so pokazali, da zasebno \u0161olstvo izvaja dober in kakovosten pouk. \nPrav tako mora biti zagotovljena tudi temeljna pravica do svobodne izbire o izobra\u017eevanju, kar pomeni, da se spo\u0161tuje pravica star\u0161ev, da zagotovijo vzgojo in izobra\u017eevanje v skladu z lastnim prepri\u010danjem. V zvezi z odlo\u010dbo Ustavnega sodi\u0161\u010da se je sestala tudi Ustavna komisija v Dr\u017eavnem zboru in na svoji seji 10. marca leto\u0161njega leta obravnavala predlog ustavnih sprememb o na\u010dinu financiranja zasebnega \u0161olstva, vendar pa je bila ta seja prekinjena zaradi precej\u0161nje razdeljenosti med poslanskimi skupinami in seveda stroko. \nMinistrica v odgovoru navaja tudi, da so se na odlo\u010ditev Ustavnega sodi\u0161\u010da odzvali \u0161tevilni zainteresirani dele\u017eniki in strokovnjaki, ki razpravljajo o posledicah odlo\u010dbe Ustavnega sodi\u0161\u010da glede financiranja zasebnih osnovnih \u0161ol. Jaz se tukaj \u0161e enkrat spra\u0161ujem, kaj je tu za razpravljati. Odlo\u010dba je bila izdana in pika. Treba jo je spo\u0161tovati, ne pa razpravljati. \nPredlagatelji nedvomno ne moremo mimo dejstva, da dr\u017eavi v prvi vrsti ne gre za financiranje, temve\u010d za ideologijo. V Slovenski demokratski stranki smo na odpravo \u017ee omenjene neustavnosti, ki jo je z odlo\u010dbo ugotovilo Ustavno sodi\u0161\u010de, vse od prevzema funkcije ministrico \u017ee ve\u010dkrat opozorili na to. Opozorili smo jo tudi, da je treba spo\u0161tovati to odlo\u010dbo Ustavnega sodi\u0161\u010da, ampak na\u0161e opozorilo je bilo vedno zavrnjeno. Na 11. nujni seji Odbora za izobra\u017eevanje 6. maja lanskega leta, kjer se je ministrica predstavila kot kandidatka za ministrico, je na vpra\u0161anje poslanske kolegice v zvezi z realizacijo odlo\u010dbe Ustavnega sodi\u0161\u010da ministrica odgovorila: \"Seveda, odlo\u010ditev je dana. \u010ce sem prav razumela, je do konca leta potrebno pripraviti na\u010din in pa izvedbo.\" Konec leta 2051 je \u017ee zdavnaj mimo, kmalu bo konec leta 2016 in v na\u0161i poslanski skupini spra\u0161ujemo ministrico, kje je zdaj ta sprememba.\nKasneje, 27. novembra lanskega leta, je ministrica za medije izjavila: \"Za to seveda potrebujemo resen razmislek, za katerega si je bolje vzeti ve\u010d \u010dasa kot pa premalo.\" Tukaj se spet spra\u0161ujem, kak\u0161en razmislek. Odlo\u010dba Ustavnega sodi\u0161\u010da je jasna, tukaj ni treba razmi\u0161ljati. \u0160e enkrat, to\u010dno se ve, kaj je treba narediti. \nV primeru dveh predlogov novel Zakona o organizaciji in financiranju vzgoje in izobra\u017eevanja s strani Slovenske demokratske stranke, najprej v decembru 2015 in nato \u0161e v marcu 2016, je ministrica Vladi predlagala v sprejem mnenje, s katerim je izrekla, da zakonska re\u0161itev, ki bi odpravila z odlo\u010dbo Ustavnega sodi\u0161\u010da ugotovljeno neustavnost, ni primerna za nadaljnjo obravnavo. Na dejstvo, da odlo\u010dba Ustavnega sodi\u0161\u010da \u0161e vedno ni realizirana, je ministrico opozorila tudi predsednica Zakonodajno-pravne slu\u017ebe Dr\u017eavnega zbora, in to takrat, ko smo obravnavali novelo Zakona o organizaciji in financiranju, to je bilo 1. junija leto\u0161njega leta. Citirala bom izjavo oziroma navedbo predstavnice Zakonodajno-pravne slu\u017ebe: \"Dr\u017eavni zbor Republike Slovenije kot zakonodajalec mora to odlo\u010dbo \u010dim prej realizirati, saj v nasprotnem primeru kr\u0161i na\u010delo pravne dr\u017eave in na\u010delo delitve oblasti. Odlo\u010dbe Ustavnega sodi\u0161\u010da so obvezne, zavezujo\u010de. Dr\u017eavni zbor Republike Slovenije jih mora pravo\u010dasno,\" ponavljam, pravo\u010dasno, \"izvr\u0161iti\". Na to opozorilo predstavnice Zakonodajno-pravne slu\u017ebe Dr\u017eavnega zbora je ministrica na seji odgovorila: \"Tu se z Zakonodajno-pravno slu\u017ebo popolnoma strinjam, ker v resnici izpolnitve ustavne odlo\u010dbe o tem predlogu ni.\" To je bilo 1. junija 2016. Kot vidimo, se ministrica samo izmika. Enkrat navaja, da je potrebna sprememba, potem, da je potreben resen razmislek, in nenazadnje, da je potrebno \u0161ir\u0161e razumevanje. Jaz ne vem, kaj je pri vsem tem treba razumeti in pa \u0161ir\u0161e razmi\u0161ljati, \u010de je pa Ustavno sodi\u0161\u010de to\u010dno povedalo, kaj je treba narediti, brez \u0161ir\u0161ega razmi\u0161ljanja. Enako nerazumna je bila tudi izjava predsednika Vlade dr. Mira Cerarja na obisku Zavoda Svetega Stanislava 19. aprila leto\u0161njega leta. Na tem obisku je predsednik Vlade dejal: \"Kot pravnik in predsednik Vlade sem nesre\u010den, ker zamujamo z izvr\u0161itvijo ustavne odlo\u010dbe. Prizadevam si, da bi jo \u010dim prej izvr\u0161ili.\" Ja, spo\u0161tovani predsednik \u2013 no, zdaj ga ni ve\u010d tu \u2013, nesre\u010dni so tudi star\u0161i teh \u0161oloobveznih otrok, ki obiskujejo zasebne \u0161ole in morajo \u0161e vedno pla\u010devati del te \u0161olnine. Prav tako so nesre\u010dne tudi zasebne \u0161ole, ker ne dobijo 100 odstotnega financiranja s strani dr\u017eave. Ministrica je v intervjuju za Ve\u010der 3. septembra leto\u0161njega leta dejala: \"Sem torej za sobivanje in ustrezno urejeno financiranje glede na ustavno odlo\u010dbo. Spo\u0161tovanje odlo\u010dbe Ustavnega sodi\u0161\u010da smo dol\u017eni zagotoviti.\" Kak\u0161no sobivanje spet in ustrezno urejeno financiranje glede na ustavno odlo\u010dbo, \u010de pa \u0161e vedno ni potrebne spremembe tega zakona? Ministrica se spet samo izmika, si pridobiva \u010das, ki pa je za star\u0161e otrok, ki obiskujejo zasebne \u0161ole, \u0161e kako dragocen, predvsem pa za njihove \u017eepe. \nZaradi vsega navedenega predlagatelji menimo, da je ministrica tako subjektivno kot objektivno odgovorna, ker pa\u010d ni naredila ni\u010d. Subjektivno je odgovorna, ker glede na svoje pristojnosti in naloge, ki jih izvr\u0161uje kot ministrica, ni upo\u0161tevala odlo\u010dbe Ustavnega sodi\u0161\u010da. Prav tako je odgovorna glede na Zakon o Vladi Republike Slovenije. Ministrica v skladu s sprejeto politiko namre\u010d vodi in predstavlja ministrstvo, daje politi\u010dne usmeritve za delo ministrstva in organov v njegovi sestavi ter opravlja druge naloge, ki jih dolo\u010da zakon in drugi predpisi. \nPredlagatelji smo mnenja, da je ministrica dr. Maja Makovec Bren\u010di\u010d odgovorna zaradi neustavnega delovanja, se pravi neizvr\u0161itve odlo\u010dbe Ustavnega sodi\u0161\u010da z dne 9. januarja 2011, takrat je ta odlo\u010dba namre\u010d stopila v veljavo. Ministrica se svojih dejanj oziroma ne dejanj tudi zaveda, kar je priznala oziroma potrdila tudi v intervjuju za \u010dasopis Ve\u010der, ko je dejala: \"Spo\u0161tovanje odlo\u010dbe Ustavnega sodi\u0161\u010da smo dol\u017eni zagotoviti.\" Kje je zdaj spet ta dol\u017enost, na katero se je za \u010dasopis sklicevala ministrica? \nPoleg subjektivne odgovornosti je ministrica v slovenskem ustavnem redu odgovora tudi objektivno, saj je vsak minister odgovoren za delo svojega ministrstva. \nMinistrica je ob imenovanju prisegla, da bo spo\u0161tovala ustavni red, da bo ravnala po svoji vesti in z vsem svojimi mo\u010dmi delovala za blaginjo Slovenije, ampak \u017eal smo pri\u010de temu, da ministrica dopu\u0161\u010da \u0161e nadaljnjo neustavnost na podro\u010dju izvajanja javno veljavnih programov osnovno\u0161olskega izobra\u017eevanja in nespo\u0161tovanja Ustave Republike Slovenije, na katero je ob imenovanju presegla. Ministrica je torej izgubila osebno integriteto, ki je nujna za opravljanje funkcije ministrice in tudi za zaupanje javnosti. \nMinistrica v svojem odgovoru na na\u0161o interpelacijo, s katero ji o\u010ditamo, da \u0161e vedno ni izvr\u0161ila odlo\u010dbe Ustavnega sodi\u0161\u010d, pravi: \"O\u010ditke, ki izhajajo iz navedene interpelacije, v celoti zavra\u010dam kot neutemeljene v vseh to\u010dkah.\" Ministrica, \u010de \u017ee ne upo\u0161tevate nas, opozicije, morate pa upo\u0161tevati odlo\u010dbe Ustavnega sodi\u0161\u010da. Vse, kar vam o\u010ditamo v tej interpelaciji, je povzeto iz odlo\u010dbe Ustavnega sodi\u0161\u010da, torej posredno trdite, da je odlo\u010dba Ustavnega sodi\u0161\u010da neutemeljena. \nV odgovoru ministrica tudi navaja, da Ustavno sodi\u0161\u010de svoje odlo\u010ditve ni sprejelo soglasno, temve\u010d s 5 glasovi za in 4 proti. Jaz zdaj ne vem, spo\u0161tovana ministrica in tudi spo\u0161tovani kolegi, ali je to nova praksa. Mogo\u010de je to nova praksa te vlade, da potem odlo\u010dbe Ustavnega sodi\u0161\u010da ne bo treba ve\u010d spo\u0161tovati ali pa upo\u0161tevati, \u010de ni sprejeta soglasno. Ministrica, to je najmanj neumnost, kar ste zapisali v vezi s tem. \nDalje. Ministrica v odgovoru na interpelacijo navaja, da je odlo\u010ditev Ustavnega sodi\u0161\u010da spro\u017eila pobudo za spremembo Ustave. To ne dr\u017ei, spo\u0161tovana ministrica. Pobudo za spremembo Ustave je spro\u017eila skupina poslank in poslancev s prvopodpisanim Matja\u017eem Hanom, in to \u017ee v februarju leta 2015, se pravi takoj po odlo\u010ditvi Ustavnega sodi\u0161\u010da, zdaj pa smo novembra 2016. Biv\u0161i predsednik Ustavnega sodi\u0161\u010da Miroslav Mozeti\u010d je ob predstavitvi poro\u010dila Ustavnega sodi\u0161\u010da za leto 2015 v zvezi s tem opozoril, da bi v primeru, da bi Dr\u017eavni zbor Republike Slovenije spremenil ustavo in financiranje zasebnih osnovnih \u0161ol uredil druga\u010de, kot so dolo\u010dili ustavni sodniki, to po njegovi oceni pomenilo, da bi Dr\u017eavni zbor zaob\u0161el odlo\u010dbo Ustavnega sodi\u0161\u010da in da je vpra\u0161anje, ali bi bilo tak\u0161no zaobitje seveda dopustno ali ne. Jaz mislim, da zdaj tukaj vsi razumemo, kaj je s tem \u017eelel povedati biv\u0161i predsednik Ustavnega sodi\u0161\u010da. \nKot \u017ee povedano, smo predlagatelji te interpelacije ministrico najmanj dvakrat opozorili na neskladje. Zato smo v proceduro vlo\u017eili tudi Predlog za spremembo Zakona o organizaciji in financiranju vzgoje in izobra\u017eevanja, ki bi upo\u0161teval odlo\u010ditev Ustavnega sodi\u0161\u010da. Ministrica pa svoje ravnanje oziroma neodzivanje opravi\u010duje z dejstvom, da je Vlada Republike Slovenije v svojem mnenju na na\u0161 predlog za odpravo neskladnosti poudarila, da predlog po celovitem re\u0161evanju vpra\u0161anja zasebnih \u0161ol temelji na novih dru\u017ebenih situacijah, ki so nastopile v zadnjem letu. Moram re\u010di, da me tudi zelo zanima, katere so te nove dru\u017ebene situacije. Ministrica v odgovoru navaja tudi, da ji je odlo\u010ditev Ustavnega sodi\u0161\u010da dobro poznana in da se zaveda, da jo je treba izvr\u0161iti. Jaz \u0161e enkrat spra\u0161ujem, spo\u0161tovana ministrica, kaj potem \u0161e vedno \u010dakate.\nZaradi vsega navedenega smo predlagatelji mnenja, da ministrica svoje funkcije ne opravlja odgovorno, zato tudi predlagamo, da se razre\u0161i s funkcije ministrica za izobra\u017eevanje, znanost in \u0161port. \nSpo\u0161tovani kolegi, danes se ne pogovarjamo, ali javno ali zasebno \u0161olstvo. Danes se pogovarjamo o tem, ali je treba spo\u0161tovati odlo\u010dbo Ustavnega sodi\u0161\u010da ali ne. Predlagatelji s to interpelacijo ministrici \u2013 \u0161e enkrat poudarjam \u2013 ne o\u010ditamo ni\u010desar drugega, kot je zapisano v odlo\u010dbi Ustavnega sodi\u0161\u010da. O\u010ditamo ji torej odgovornost za neukrepanje in zavla\u010devanje pri pripravi novele zakona, ustvarjanje neenakosti pred zakonom in opustitev dol\u017enega ravnanja pri izvr\u0161evanju politi\u010dne funkcije, ki ima za posledico izgubljeno zaupanje v institucije pravne in socialne dr\u017eave. \nSpo\u0161tovani kolegi poslanci, \u0161e enkrat. \u010ce ste mnenja, da je treba spo\u0161tovati ustavo in zakone, verjamem, da boste na\u0161o interpelacijo danes podprli. Hvala lepa.",
        "Hvala za besedo. Lep pozdrav vsem. Moram re\u010di, gospa Pirnat, da ko sem vas poslu\u0161ala v uvodni obrazlo\u017eitvi ste zelo prepri\u010dljivo nanizali oziroma povedali kaj vse delate, kaj vse ste storili in kaj vse boste storili \u0161e do 31. januarja. Moram re\u010di, \u010de ne bi poznala delo va\u0161ega ministrstva, tole bi takoj kupila danes in dvignila na kocu roko. \n (nadaljevanje) Poglejte, \u010de pa pogledamo, kaj ste v teh dveh letih in pol naredili na svojem podro\u010dju, se pravi, iz ukrepov koalicijske pogodbe niti enega ukrepa niste uresni\u010dili, iz normativnega dela programa Vlade izmed 17 zakonov, ki so bili na\u010drtovani, ki jih je ministrstvo na\u010drtovalo, da jih bo sprejelo v letih 2015 in 2016, se pravi, od 17 so bili sprejeti 4. Torej, tej va\u0161i uvodni obrazlo\u017eitvi nikakor ne morem verjeti. \nMoram re\u010di, da me mo\u010dno skrbi razprava gospoda Mezka, ki pravi, da je poslovanje javnih zdravstvenih zavodov v 9-mese\u010dju slab\u0161e od pri\u010dakovanega rezultata in da bo poslovanje javnih zdravstvenih zavodov konec leta \u0161e slab\u0161e, kot se je pri\u010dakovalo. \u0160koda, da smo z va\u0161e strani v razpravi sli\u0161ali le neke izgovore, kaj je vplivalo na te slabe rezultate, nismo pa sli\u0161ali nobene konkretne zaveze oziroma nobenega konkretnega ukrepa, kaj bi se naj naredilo, tudi na pobudo Zdru\u017eenja javnih zdravstvenih zavodov. Strinjam se, predsednik, z va\u0161o ugotovitvijo, da za to trenutno stanje, ki je na podro\u010dju zdravstva, ni krivo samo to ministrstvo in ta Vlada. Ampak dejstvo je, poglejte, da imamo dolge \u010dakalne vrste, da so izgube v javnih zdravstvenih zavodih vse ve\u010dje, imamo korupcijo, nedvomno, politi\u010dno kadrovanje, ni sistemskih re\u0161itev. Moram re\u010di, da je pa k temu poslab\u0161anju oziroma k tem negativnim trendom na podro\u010dju zdravstva nedvomno pripomoglo Ministrstvo za zdrave oziroma ta Vlada. \nV Slovenski demokratski stranki \u017ee dve leti in pol nenehno opozarjamo, da so potrebne sistemske re\u0161itve, se pravi, zakonodaja; da je treba kon\u010dno dolo\u010diti javno mre\u017eo na vseh podro\u010djih, na primarnem, sekundarnem in tako naprej; da je treba dolo\u010diti standarde, da je treba dolo\u010diti tudi standarde za pla\u010dilo storitev izvajalcem; da je treba preoblikovati javne zavode v skladu s pravom EU in kar je verjetno del te rak rane, teh izgub javnih zdravstvenih zavodov, in sicer, da je spremeniti zakonodajo v smislu, da se da ve\u010d pristojnosti direktorjem javnih zdravstvenih zavodov, po drugi strani pa od njih zahtevati ve\u010d odgovornosti, ne pa da direktor ni odgovoren za poslovanje nekega javnega zdravstvenega zavoda. Dejstvo je, kar smo sli\u0161ali \u017ee v uvodni obrazlo\u017eitvi, da so rezultati poslovanja javnih zdravstvenih zavodov za prvo polletje izredno slabi, \u010de jih primerjamo z letom 2015. V letu 2015 kar 23 bolni\u0161nic ustvarilo prese\u017eek v vi\u0161ini 10,4 milijona in samo 3 bolni\u0161nice so imele primanjkljaj v vi\u0161ini 9,8 milijona, od tega 6 milijonov UKC Ljubljana. \u010ce pa pogledamo prvo polletje leto\u0161njega leta, ima pa samo 12 bolni\u0161nic prese\u017eek 2,8 milijona in \u017ee kar 14 bolni\u0161nic primanjkljaj v vi\u0161ini 19,3 milijona in od tega samo UKC Ljubljana 12,7 milijona evrov. Zelo zaskrbljujo\u010da je napoved gospoda Mezka, ki pravi, da so rezultati za 9-mese\u010dje \u0161e slab\u0161i, rezultati ob koncu leta pa bodo nedvomno \u0161e slab\u0161i. \nNekateri ste v razpravi te izgube javnih zdravstvenih zavodov nekako opravi\u010devali z zni\u017eanjem cen storitev Zavoda za zdravstveno zavarovanje, nekateri z napredovanjem in \u0161e nekatere druge vzroke sem sli\u0161ala. Ampak, poglejte, meni se tu \u0161e kako zastavlja vpra\u0161anje, zakaj samo nekateri javni zdravstveni zavodi. Ali pa, \u010de pogledamo naprej, kaj pa \n (nadaljevanje) koncesionarji. Poglejte, koliko koncesionar, preden za\u010dne delati, opravljati svojo dejavnost, koliko vlo\u017ei v nabavo opreme, prostora. Tule imam podatek, da dru\u017einski zdravnik, preden za\u010dne s svojim delom, 30 tiso\u010d evrov, zobozdravnik 63 tiso\u010d evrov, specialist 360 tiso\u010d evrov. Ve\u010dina teh koncesionarjev ob koncu leta pla\u010da \u0161e od pozitivnega poslovanja davek na dobi\u010dek. Ampak, poglejte, prav zanima me, \u010de mi zna kdo povedati, koliko koncesionarjev ob koncu leta posluje negativno, to bi bil zame zanimiv podatek. \nKje je tu odgovornost, kot sem \u017ee prej rekla, direktorjev javnih zdravstvenih zavodov. Pa ne samo teh, nedvomno bi jaz tu vsaj del\u010dek te odgovornosti terjala tudi od svetov javnih zdravstvenih zavodov, pa tudi s strani ministrstva. Kot sem \u017ee rekla prej, nedvomno bi bilo poslovanje teh zavodov druga\u010dno, \u010de bi direktor javnega zdravstvenega zavoda s tem denarjem, ki ga ima na razpolago, delal tako, kot da bi bil njegov. Nedvomno bi se pri takem ravnanju na\u010din nabave materiala spremenil, verjetno tudi naro\u010dil za dolo\u010dene nabave ne bi drobil in material se ne bi kupovalo na naro\u010dilnice, ampak preko javnih razpisov, kar bi pa seveda pomenilo tudi ni\u017ejo ceno materiala. Ampak, \u017eal, se te nabave ve\u010dinoma delajo na podlagi naro\u010dilnic, kar je \u0161e slab\u0161e, preko znanstev, velikokrat pa tudi obstaja sum, da za svoj ra\u010dun. Ampak, poglejte, to mi govorimo \u017ee, mislim, da smo dali prvo pobudo glede korupcije oziroma priporo\u010dila \u017ee v za\u010detku lanskega leta. Ampak tu se samo govori, mi premlevamo in premlevamo to na seji Dr\u017eavnega zbora, nih\u010de pa ne ukrene ni\u010desar. \u0160e najbolj me moti to, ker nas ministrstvo poslu\u0161a, redkokdaj, \u0161koda, pride ministrica, in zdi se mi, da ministrstvo malo prisluhne, zami\u017ei na eno oko in karavana gre po isti poti naprej. \nZanima me, na primer, kaj je naredilo ministrstvo oziroma sam UKC \u2013 \u0161koda, da danes ni predstavnika oziroma direktorja UKC, mislim, da je bil tudi vabljen -, ob taki napovedi rde\u010dih \u0161tevilk oziroma taki polletni napovedi izgube UKC. Mislim, da bi tu moral zasvetiti rde\u010d alarm in da bi morali tako direktor bolni\u0161nice oziroma UKC, svet zavoda in ministrstvo nekaj narediti, ampak, \u017eal, vemo, da se ni naredilo na tem ni\u010desar. Direktor UKC vehementno v svoji informaciji o zaposlovanju za obdobje januar-junij 2016 ob koncu napove, da bodo ob koncu leta odhodki presegli realizirane prihodke za 20 milijonov evrov, in bom rekla zelo grdo, \"i nikome ni\u0161ta\". Kje je tu svet zavoda? Pa ministrica sprejema take protokole in ne vem kak\u0161ne vse lastnosti bi naj imeli ti \u010dlani oziroma novi predstavniki sveta javnih zavodov, ampak u\u010dinka pa nedvomno nobenega. Bo pa\u010d izguba, saj to ne gre direktno iz mojega \u017eepa, saj gre to s strani davkopla\u010devalcev in gremo naprej. \n (nadaljevanje) V tej razpravi je bilo tudi, kot sem \u017ee prej rekla, nekako re\u010deno, da pa\u010d Zavod za zdravstveno zavarovanje je zmanj\u0161al cene storitve za 9,9 %, res, da jih je lani nekaj pove\u010dal in tako naprej, ampak jaz se dobro spomnim razprav tule prej\u0161njega direktorja Zavoda za zdravstveno zavarovanje, gospoda Fakina, glede cen storitev, pla\u010dila storitev. In mislim, da je gospod Fakin mogo\u010de kdaj prav dobro vedel, zakaj se ni strinjal, da se cene teh zdravstvenih storitev pove\u010dajo. \u0160e enkrat bom to rekla, ne gre mi v ra\u010dun oziroma mogo\u010de mi bo kdo pomagal, \u010de me bo prepri\u010dal, v redu, bom vesela, v ra\u010dun, da nekateri javni zavodi poslujejo kljub temu na nuli ali pa pozitivno ali pa koncesionarji ob pla\u010dilu oziroma ob neki ceni dolo\u010dene storitve, ki jo dobijo s strani Zavoda za zdravstveno zavarovanje. Seveda pa bi rada poudarila, da bi pa po moji logiki bilo tudi treba, da bi se s strani Zavoda za zdravstveno zavarovanje \u2013 ne, da ta zavarovalnica samo pla\u010da nek ra\u010dun izvajalcu, meni se zdi, da bi bilo tu potrebno, da bi tudi zavarovalnica preverila ta ra\u010dun in najmanj, kar je, da bi tudi primerjala cene dolo\u010denega materiala, \u010de \u017ee cen storitev ne. Glede na to se mi zdi tudi zelo logi\u010dno, da bi bilo treba poleg vseh aktivnosti na Zavodu za zdravstveno zavarovanje, le-ta bi moral nekako uvesti oziroma pripraviti standarde za pla\u010dilo cen storitev izvajalcem. In v tem primeru, sem prepri\u010dana, ne bi nekateri javni zdravstveni zavodi dobili tudi do 100 ali ve\u010d kot 100 % ve\u010d pla\u010dano storitev kot drugi javni zdravstveni zavodi. Ampak o teh standardih za neko enotno pla\u010dilo zdravstvenih storitev se govori \u017ee dolgo in moram re\u010di, da me je po\u010dasi za\u010delo skrbeti, v \u010digavem interesu je, da se pa\u010d ti standardi ne pripravijo. \u010ce se zdaj pripravljajo ali pa \u010de so pripravljeni, pa da \u017eivim v zmoti, bi prosila, da mi to poveste. \nKot sem \u017ee rekla, izgube zdravstvenih zavodov se pove\u010dujejo, pove\u010dujejo se \u010dakalne vrste, v enem letu za ve\u010d kot 30 % oziroma v zadnjih \u0161tirih, zdaj \u017ee petih letih ve\u010d kot enkrat in stanje na podro\u010dju zdravstva je zelo zaskrbljujo\u010de. Ob tem bi rada poudarila, kar v na\u0161i stranki vedno poudarjamo, da na\u0161i dr\u017eavljani oziroma Slovenci imamo veliko sre\u010do, da je stroka dobra. Stroka namre\u010d sodi na marsikaterem podro\u010dju v sam svetovni vrh in tudi na\u0161i dr\u017eavljani so \u0161e kako zadovoljni z opravljenimi storitvami, seveda, \u010de imajo to sre\u010do, da pridejo na vrsto. Poleg vseh teh rde\u010dih \u0161tevilk, ki jih prikazujejo javni zdravstveni zavodi, mislim, da bi tu bil \u0161e kako potreben nek izra\u010dun, koliko pa v bistvu bolan \u010dlovek stane dr\u017eavo, ne samo opravljena storitev v bolni\u0161nici, tu je potem \u0161e primanjkljaj oziroma manko njegova bolni\u0161ka odsotnost, ki gre najprej na ra\u010dun delodajalca, potem na ra\u010dun Zavoda za zdravstveno zavarovanje, potem rehabilitacija in tako naprej. To bi tudi bilo mogo\u010de dobro sli\u0161ati s strani ministrstva, \u010de ima kakr\u0161nekoli take podatke. \nVelikokrat smo ministrico poslu\u0161ali \u2013 \u0161e enkrat bom ponovila, \u0161koda, da je danes ni z nami, \n(Nadaljevanje) da pa\u010d ni odgovorna sama za poslovanje javnih zdravstvenih zavodov. Ampak po drugi strani pa je ravno ministrica za medije podala izjavo, da se je takoj ob nastopu mandata za\u010dela ukvarjati s sanacijo prihodkovne strani javnih zdravstvenih zavodov. Sedaj jaz ne razumem, se bo ministrica kon\u010dno odlo\u010dila ali je odgovorna za poslovanje javnih zdravstvenih zavodov ali ni, definitivno pa je, ker dr\u017eava je ustanoviteljica bolni\u0161nic in s strani dr\u017eave oziroma Vlade so imenovani tudi \u010dlani svetov zavodov. Najve\u010dkrat se tudi na pobudo ministrice oziroma ministrstva izbere tudi kandidat za direktorja, kar smo bili pri\u010da v mnogih primerih v lanskem letu, se pravi, pri UKC Ljubljana, poznamo najprej primer Bari\u010di\u010d, ki ga je ministrica \u0161e kako zagovarjala, njegove sposobnosti in tako naprej, da o gospodu Kopa\u010du, sedanjemu direktorju UKC sploh ne izgubljam besed. Sedaj, znano je dejstvo tudi, \u010de \u0161e ostanem malo pri UKC, ki nekako izkazuje najve\u010djo izgubo za lansko leto. Poglejte, lansko leto smo opozarjali tako na seji mati\u010dnega odbora kot tudi na seji Dr\u017eavnega zbora, da je UKC Ljubljana sklepal pogodbe o dobavi na reverz oziroma, da je sklepala pogodbe o dobavi na reverz oseba, ki ni bila zakonit zastopnik UKC in to pogodbo je sklepala en mesec preden je bil sprejet sklep o nabavi. Na to smo \u017ee v lanskem letu opozorili, ampak zanima me kaj je storilo ministrstvo, \u010de boste znali na to odgovoriti, bom zelo vesela. Znano je pa, da je \u0161lo v teh primerih tudi za velike zaslu\u017eke s strani servisiranja te opreme potem. Sedaj mediji so tudi na veliko pisali in \u0161e pi\u0161ejo, da se denar preko javnih zdravstvenih zavodov prena\u0161a seveda na razli\u010dne dobavitelje, in da ti izvajajo pritisk vplivnih posameznikov na nabavo dolo\u010dene opreme in pa materialov. Ta izjava nam je vsem dobro znana. To je rekla, gospa \u010cokl na seji Komisije za nadzor javnih financ, ampak zgodilo se ni ni\u010d.\n Sedaj, \u010de se ustavim pri skupnih javnih naro\u010dilih. Ministrstvo je pripravilo, \u017ee za\u010delo s pripravo nekih protokolov za podro\u010dje javnih razpisov v letu 2015 in prvi javni razpis pripravilo tudi v letu 2015. Zanima me pa, koliko javnih razpisov je bilo do sedaj izpeljano. Kolikor mi je znano, samo eden ali pa \u0161e ta ne do konca. \nZanima me tudi kaj je ministrstvo naredilo glede stro\u0161kov vzdr\u017eevanja informacijskih sistemov v UKC. Ali je kaj reagiralo na to drago vzdr\u017eevanje? Znano je, da ministrstvo ni reagiralo, \u010deprav bi po mojem mnenju \u0161e kako lahko. Poglejte, da zavodi poslujejo negativno, definitivno ima na to vpliv tudi na vrat na nos sprejem oziroma, ja, pravilnik o nujni medicinski pomo\u010di. Mi smo \u017ee takrat opozarjali na vse nev\u0161e\u010dnosti, ki se bodo dogajale in takrat smo tudi opozarjali, da je potrebno oziroma da urgentni centri nimajo znotraj vklju\u010denih pediatri\u010dnih urgentnih centrov. Mi smo na to, mi in pa stroka je na to opozarjala \u017ee v letu 2015, ampak \u010deprav je ministrica rekla, da je to izvedela \u0161ele marca 2016 in poglejte, tak na\u010din sprejemanja samega pravilnika brez tega, da bi bila pripravljena neka finan\u010dna, kadrovska, organizacijska shema oziroma konstrukcija, smo bili mnenja, da je to nekako projekt, ki se je iz finan\u010dnega vidika nekako neprijazen do prora\u010duna dr\u017eave. In prav zaskrbljujo\u010de je dejstvo, kar je tudi gospa dr\u017eavna sekretarka rekla, da se \u0161ele sedaj ta komisija, neka komisija sestavi in pripravlja neke normative za pla\u010dilo storitev. Toliko za enkrat z moje strani. Jaz verjamem, da se bodo moji kolegi osredoto\u010dili na samo revizijsko poro\u010dilo in na aktivnosti, ki bi jih moralo izvesti ministrstvo, ki pa jih \u0161e \u017eal ni oziroma se ni odzvalo niti na, negativno odzvalo na odzivno poro\u010dilo. Za konec bi rada rekla to, da dejstvo je, da korupcija iz\u010drpava zdravstvo, javni denar se preteka v privat \u017eepe, bolnice so v rde\u010dih \u0161tevilkah, posledice \u010duti tudi na\u0161 prora\u010dun in seveda, \u017eal, posledice \u010dutijo tudi na\u0161i dr\u017eavljani. Hvala lepa.",
        "Poglejte, drugi odstavek tega \u010dlena govori \"Dovoljenje za organiziranje priro\u010dne zaloge zdravil izda ob\u010dina.\" Poglejte, kaj ima ob\u010dina s tem? Mi predlagamo \u010drtanje tega odstavka."
    ]
    """

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    speeches_queryset = Speech.getValidSpeeches(fdate)
    content = speeches_queryset.filter(speaker__id=person_id,
                                       start_time__lte=fdate)
    content = list(content.values_list('content', flat=True))
    return JsonResponse(content, safe=False)


def getSpeechesOfMPbyDate(request, person_id, date_=None):
    """Returns all speeches of all MP to specific date."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker__id=person_id,
                                                 start_time__lte=fdate)
    dates = speeches_queryset.order_by("start_time").dates("start_time", "day")
    content = [{"date": date.strftime(settings.API_DATE_FORMAT),
                "speeches": [speech.content
                             for speech in speeches_queryset.filter(Q(start_time__gte=date) |
                                                                    Q(start_time__lte=date + timedelta(days=1)),
                                                                    speaker__id=person_id)]}
               for date in dates]

    return JsonResponse(content, safe=False)



def getAllSpeechesOfMPs(request, date_=None):
    """
    * @api {get} getAllMPsSpeeches/{?date}/ All MPs' speeches
    * @apiName getAllMPsSpeeches
    * @apiGroup MPs
    * @apiDescription This function returns all MPs' speeches up until today (or an optional date)
      as an array of objects.
    * @apiParam {date} date Date up until which speeches should be returned.

    * @apiSuccess {Object} speech A speech.
    * @apiSuccess {String} speech.valid_from Start time of the speech's validity.
    * @apiSuccess {String} speech.start_time Start time of the speech's transcript.
    * @apiSuccess {String} speech.valid_to End time of the speech's validity (expiration date).
    * @apiSuccess {Integer} speech.order The speech's order in its transcript.
    * @apiSuccess {String} speech.content The speech's content.
    * @apiSuccess {Integer} speech.session The speech's session Parladata id.
    * @apiSuccess {Integer} speech.speaker The speech's speaker Parladata id.
    * @apiSuccess {String} speech.end_time Placeholder field for a piece of data we do not
      possess yet. Returns null.
    * @apiSuccess {Integer} speech.party The speech's speaker's party Parladata id.
    * @apiSuccess {Integer} speech.id The speech's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllMPsSpeeches
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllMPsSpeeches/5.2.2017

     * @apiSuccessExample {json} Example response:
     [{
        "valid_from": "2014-08-01T02:00:00",
        "start_time": "2014-08-01T02:00:00",
        "valid_to": "2017-02-06T01:59:52.624",
        "order": 30,
        "content": "Najlep\u0161a hvala.\nIzvolite.",
        "session": 7610,
        "speaker": 33,
        "end_time": null,
        "party": 1,
        "id": 880492
      }, {
        "valid_from": "2014-08-01T02:00:00",
        "start_time": "2014-08-01T02:00:00",
        "valid_to": "9999-12-31T23:59:59.999",
        "order": 180,
        "content": "Hvala lepa, ponovno. \nPoglejte, gospa predsedujo\u010da, vi ste povedali, da ste na osnovi ustne obrazlo\u017eitve Zakonodajno-pravne slu\u017ebe napisali tisto, kar imate in kar berete. Nas ta va\u0161a interpretacija ne zadovolji, ker se mi zdi nekorektno, da sku\u0161a predsedujo\u010di skupaj z generalno sekretarko Dr\u017eavnega zbora tudi zdaj, ko za to ni potrebe, sku\u0161a stvari peljati na nek neposlovni\u0161ki na\u010din in nas peljati preko to\u010dk dnevnega reda v dvomu, da je zadeva pripravljena v skladu z zakonom. Mislim, da je to nekorektno. \nPrva naloga predsedujo\u010dega Dr\u017eavnega zbora in generalne sekretarke Dr\u017eavnega zbora je, da se postopki speljejo korektno, da na njih ni sence dvoma, da nih\u010de ne dvomi, da je karkoli v tem postopku narobe. In zato predlagamo oziroma zahtevamo, da dobimo pisno mnenje Zakonodajno-pravne slu\u017ebe. Zato zahtevamo. Tisto, kar so na\u0161e obveznosti, ne skrbite, jih bomo izpolnili , ko bo \u010das za to in ko bo soglasje v Dr\u017eavnem zboru za to. Ta trenutek ni. Zato predlagam, da, ne vem, namesto, da mu\u010dite dr\u017eavni zbor, da naredite to prekinitev, da naredite tisto, kar se pri\u010dakuje od predsedujo\u010dega, to se pravi, da zagotovi vse podlage, ki so potrebne za to, da se pri tej to\u010dki opravi odlo\u010danje, da se opravi odlo\u010danje tudi pri naslednjih dveh to\u010dkah dnevnega reda, to, da bomo imeli mandatno komisijo, ki bo sestavljena res v skladu z zakonom, in da bodo odlo\u010ditve skladne z zakonom o poslancih. To materijo ureja ve\u010d aktov, poslovnik je en od aktov, ampak neposredno dolo\u010dbo o tem, kako mora biti Mandatno-volilna komisija sestavljena, pa dolo\u010da zakon. Vi nam ne govoriti in razlagati pravic poslanske skupine in poslancev, mi zahtevamo interpretacijo oziroma mnenje Zakonodajno-pravne slu\u017ebe v zvezi z dolo\u010dbo 7. \u010dlena Zakona o poslancih. Mi ne \u017eelimo va\u0161e interpretacije, gospa, mi ne \u017eelimo interpretacije generalne sekretarke Dr\u017eavnega zbora, mi \u017eelimo interpretacijo, obrazlo\u017eitev, obrazlo\u017eeno mnenje Zakonodajno-pravne slu\u017ebe Dr\u017eavnega zbora. In ni\u010d drugega. Od tam naprej pa se bomo odlo\u010dili, kako bomo ravnali, ko bomo to mnenje dobili. Hvala lepa.",
        "session": 6684,
        "speaker": 78,
        "end_time": null,
        "party": 5,
        "id": 597620
      }]
    """

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    parliamentary_group = Organization.objects.filter(classification=PS)
    members = list(set(Membership.objects.filter(organization__in=parliamentary_group).values_list("person__id", flat=True)))

    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker__in=members,
                                                 start_time__lte=fdate)
    speeches = [model_to_dict(speech, fields=[field.name for field in speech._meta.fields], exclude=[]) for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


def getMPParty(request, person_id):
    """Returns party of specific MP."""

    person = Person.objects.get(id=person_id)
    party = [{'name': membership.organization.name,
              'id': membership.organization.id,
              'acronym': membership.organization.acronym}
             for membership
             in person.memberships.all()
             if membership.organization.classification == PS]

    out = {'name': party[0]['name'],
           'id': party[0]['id'],
           'acronym': party[0]['acronym']}

    return JsonResponse(out)


def getNumberOfSeatsOfPG(request, pg_id):
    """Returns number of seats in each PG."""

    value = dict()
    parliamentary_group = Organization.objects.filter(classification=PS,
                                                      id=int(pg_id))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    data = {pg.id: len([member.person.id for member in members.filter(organization=pg)]) for pg in parliamentary_group}
    value = {int(pg_id): data[int(pg_id)]}

    return JsonResponse(value, safe=False)


def getBasicInfOfPG(request, pg_id, date_):
    """Returns basic info of PG."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    viceOfPG = []
    data = dict()
    listOfVotes = []
    parliamentary_group = Organization.objects.filter(classification=PS,
                                                      id=pg_id)

    members = Membership.objects.filter(Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        organization__id=parliamentary_group)

    if len(Post.objects.filter(Q(start_time__lte=fdate) |
                               Q(start_time=None),
                               Q(end_time__gte=fdate) |
                               Q(end_time=None),
                               membership__organization=parliamentary_group,
                               label="v")) == 1:
        headOfPG = Post.objects.get(Q(start_time__lte=fdate) |
                                    Q(start_time=None),
                                    Q(end_time__gte=fdate) |
                                    Q(end_time=None),
                                    membership__organization=parliamentary_group,
                                    label="v").membership.person.id
    else:
        headOfPG = None

    if len(Post.objects.filter(Q(start_time__lte=fdate) |
                               Q(start_time=None),
                               Q(end_time__gte=fdate) |
                               Q(end_time=None),
                               membership__organization=parliamentary_group,
                               label="namv")) > 0:

        for post in Post.objects.filter(Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        membership__organization=parliamentary_group,
                                        label="namv"):

            viceOfPG.append(post.membership.person.id)
    else:
        viceOfPG = None

    numberOfSeats = len(members)

    for a in members:
        if a.person.voters is not None:
            listOfVotes.append(a.person.voters)
        else:
            listOfVotes.append(0)

    allVoters = sum(listOfVotes)
    if len(Link.objects.filter(organization=parliamentary_group,
                               note='FB')) > 0:
        FB = Link.objects.filter(organization=parliamentary_group,
                                 note='FB')[0].url
    else:
        FB = None
    if len(ContactDetail.objects.filter(organization=parliamentary_group,
                                        label='Mail')) > 0:
        mail = ContactDetail.objects.filter(organization=parliamentary_group,
                                            label='Mail')[0].value
    else:
        mail = None
    if len(Link.objects.filter(organization=parliamentary_group,
                               note='TW')) > 0:
        twitter = Link.objects.filter(organization=parliamentary_group,
                                      note='TW')[0].url

    else:
        twitter = None
    data = {"HeadOfPG": headOfPG,
            "ViceOfPG": viceOfPG,
            "NumberOfSeats": numberOfSeats,
            "AllVoters": allVoters,
            "Mail": mail,
            "Facebook": FB,
            "Twitter": twitter
            }

    return JsonResponse(data, safe=False)


def getAllPGs(request, date_=None):
    """Returns all PGs."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    parliamentary_group = Organization.objects.filter(classification=PS)
    parliamentary_group = parliamentary_group.filter(Q(founding_date__lte=fdate) |
                                                     Q(founding_date=None),
                                                     Q(dissolution_date__gte=fdate) |
                                                     Q(dissolution_date=None))
    data = {pg.id: {'name': pg.name,
                    'acronym': pg.acronym,
                    'id': pg.id,
                    'is_coalition': True if pg.is_coalition == 1 else False} for pg in parliamentary_group}

    return JsonResponse(data)


def getAllPGsExt(request):
    """Reutrns all PGs with founded and disbanded dates."""

    parliamentary_group = Organization.objects.filter(classification=PS)
    data = {pg.id: {'name': pg.name,
                    'acronym': pg.acronym,
                    'founded': pg.founding_date,
                    'disbanded': pg.dissolution_date} for pg in parliamentary_group}

    return JsonResponse(data, safe=False)

def getAllOrganizations(requests):
    """Returns all organizations."""

    org = Organization.objects.all()
    data = {pg.id: {'name': pg.name,
                    'classification': pg.classification,
                    'acronym': pg.acronym,
                    'is_coalition': True if pg.is_coalition == 1 else False} for pg in org}

    return JsonResponse(data)


def getAllSpeeches(requests, date_=None):
    """Returns all speeches."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches = speeches_queryset.filter(start_time__lte=fdate)
    for speech in speeches:
        data.append(model_to_dict(speech,
                                  fields=[field.name for field in speech._meta.fields],
                                  exclude=[]))

    return JsonResponse(data, safe=False)


def getAllVotes(requests, date_):
    """Returns all votes."""

    fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date() + timedelta(days=1) - timedelta(minutes=1)
    data = []

    votes = Vote.objects.filter(start_time__lte=fdate).order_by("start_time")
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
    """Returns all ballots."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    data = [model_to_dict(ballot,
                          fields=['id', 'vote', 'voter', 'option'], exclude=[])
            for ballot in Ballot.objects.filter(vote__start_time__lte=fdate)]

    return JsonResponse(data, safe=False)


def getAllPeople(requests):
    """Returns all people."""
    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    data = []
    pg = ''
    person = Person.objects.all()
    for i in person:
        membership = Membership.objects.filter(person=i.id,
                                               organization=parliamentary_group)
        for me in membership:
            pg = me.organization.name
        data.append({'id': i.id,
                     'name': i.name,
                     'membership': pg,
                     'classification': i.classification,
                     'family_name': i.family_name,
                     'given_name': i.given_name,
                     'additional_name': i.additional_name,
                     'honorific_prefix': i.honorific_prefix,
                     'honorific_suffix': i.honorific_suffix,
                     'patronymic_name': i.patronymic_name,
                     'sort_name': i.sort_name,
                     'email': i.email,
                     'gender': i.gender,
                     'birth_date': str(i.birth_date),
                     'death_date': str(i.death_date),
                     'summary': i.summary,
                     'biography': i.biography,
                     'image': i.image,
                     'district': '',
                     'gov_id': i.gov_id,
                     'gov_picture_url': i.gov_picture_url,
                     'voters': i.voters,
                     'active': i.active})
        pg = None

    return JsonResponse(data, safe=False)


def motionOfSession(request, id_se):
    """Returns all votes of specific Session."""

    data = {}
    tab = []
    data = []
    allIDs = Session.objects.values('id')
    for i in allIDs:
        tab.append(i['id'])
    if int(id_se) in tab:
        votes = Vote.objects.filter(session__id=id_se)
        if votes:
            for vote in votes:
                motion = vote.motion
                links = motion.links.all()
                links_list = [{'name': link.name, 'url': link.url}
                              for link in links]
                data.append({'id': motion.id,
                             'vote_id': vote.id,
                             'text': motion.text,
                             'result': False if motion.result == '0' else True,
                             'tags': map(smart_str, vote.tags.names()),
                             'doc_url': links_list})
        else:
            data = []
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse([], safe=False)


def getVotesOfSession(request, id_se):
    """Returns all votes of specific Session."""

    fdate = Session.objects.get(id=str(id_se)).start_time
    mems_qs = Membership.objects.filter(Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        organization__classification__in=PS_NP)
    memberships = {mem.person.id: {'org_id': mem.organization.id,
                                   'org_acronym': mem.organization.acronym}
                   for mem in mems_qs}
    mems_ids = memberships.keys()
    data = []
    for bal in Ballot.objects.filter(vote__session__id=str(id_se)):
        if bal.voter.id in mems_ids:
            data.append({'mo_id': bal.vote.motion.id,
                         'mp_id': bal.voter.id,
                         'Acronym': memberships[bal.voter.id]['org_acronym'],
                         'option': bal.option,
                         'pg_id': memberships[bal.voter.id]['org_id']})
        else:
            print 'No memberships: ', bal.voter.id
    return JsonResponse(data, safe=False)


def getVotesOfMotion(request, motion_id):
    """Returns all ballots of specific motion."""

    data = []
    vote = Vote.objects.get(id=motion_id)
    motion = vote.motion
    for bal in Ballot.objects.filter(vote=vote):
        mem = Membership.objects.get(Q(end_time__gte=vote.start_time) |
                                     Q(end_time=None),
                                     Q(start_time__lte=vote.start_time) |
                                     Q(start_time=None),
                                     person__id=bal.voter_id,
                                     organization__classification__in=PS_NP)
        data.append({'mo_id': motion.id,
                     "mp_id": bal.voter_id,
                     "Acronym": mem.organization.acronym,
                     "option": bal.option,
                     "pg_id": mem.organization.id})

    return JsonResponse(data, safe=False)


def getNumberOfPersonsSessions(request, person_id, date_=None):
    """Returns number of MPs attended Sessions."""

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
    """Returns number of formal speeches of specific MP."""

    url = 'http://isci.parlameter.si/filter/besedo%20dajem?people=' + person_id

    person = Person.objects.get(id=int(person_id))

    dz = Organization.objects.get(id=95)

    if len(person.memberships.filter(organization=dz).filter(Q(label='podp') |
                                                             Q(label='p'))) > 0:
        r = requests.get(url).json()
        return HttpResponse(int(r['response']['numFound']))
    else:
        return HttpResponse(0)


def getExtendedSpeechesOfMP(request, person_id):
    """Returns speeches of specific MP."""

    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker__id=person_id)

    speeches = [{'content': speech.content,
                 'speech_id': speech.id,
                 'speaker': speech.speaker.id,
                 'session_name': speech.session.name,
                 'session_id': speech.session.id}
                for speech in speeches_queryset]

    return JsonResponse(speeches, safe=False)


def getTaggedVotes(request, person_id):
    """Returns ballots for specific MP from working bodies."""

    tags = ['Komisija za nadzor javnih financ',
            'Kolegij predsednika Državnega zbora',
            'Komisija za narodni skupnosti',
            'Komisija za odnose s Slovenci v zamejstvu in po svetu',
            'Komisija za poslovnik',
            'Mandatno-volilna komisija',
            'Odbor za delo, družino, socialne zadeve in invalide',
            'Odbor za finance in monetarno politiko',
            'Odbor za gospodarstvo',
            'Odbor za infrastrukturo, okolje in prostor',
            'Odbor za izobraževanje, znanost, šport in mladino',
            'Odbor za kmetijstvo, gozdarstvo in prehrano',
            'Odbor za kulturo',
            'Odbor za notranje zadeve, javno upravo in lokalno samoupravo',
            'Odbor za obrambo',
            'Odbor za pravosodje',
            'Odbor za zadeve Evropske unije',
            'Odbor za zdravstvo',
            'Odbor za zunanjo politiko',
            'Preiskovalna komisija o ugotavljanju zlorab v slovenskem bančnem sistemu ter ugotavljanju vzrokov in',
            'Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investiciji',
            'Ustavna komisija',
            'Proceduralna glasovanja',
            'Zunanja imenovanja',
            'Poslanska vprašanja',
            'Komisija za nadzor obveščevalnih in varnostnih služb',
            'Preiskovalne komisije']

    votes_queryset = Vote.objects.filter(tags__name__in=tags)

    person = Person.objects.filter(id=int(person_id))[0]
    ballots = person.ballot_set.filter(vote__in=votes_queryset)

    ballots_out = [{'option': ballot.option,
                    'vote': {'name': ballot.vote.name,
                             'motion_id': ballot.vote.motion.id,
                             'session_id': ballot.vote.session.id,
                             'id': ballot.vote.id,
                             'result': ballot.vote.result,
                             'date': ballot.vote.start_time,
                             'tags': [tag.name
                                      for tag in ballot.vote.tags.all()]}}
                   for ballot in ballots]

    return JsonResponse(ballots_out, safe=False)


def getMembersOfPGsRanges(request, date_=None):
    """
    Returns all memberships(start date, end date and members
    in this dates) of all PGs from start of mandate to end date
    which is an argument of method.
    """

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    tempDate = settings.MANDATE_START_TIME.date()
    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(organization__in=parliamentary_group)

    pgs_ids = parliamentary_group.values_list("id", flat=True)
    out = {(tempDate + timedelta(days=days)): {grup: []
                                               for grup
                                               in pgs_ids}
           for days in range((fdate - tempDate).days + 1)}

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
        for days in range((end_time - start_time).days + 1):
            day = out[(start_time + timedelta(days=days))]
            day[member.organization.id].append(member.person.id)

    keys = out.keys()
    keys.sort()
    outList = [{"start_date": keys[0].strftime(settings.API_DATE_FORMAT),
                "end_date": keys[0].strftime(settings.API_DATE_FORMAT),
                "members": out[keys[0]]}]
    for key in keys:
        if out[key] == outList[-1]["members"]:
            outList[-1]["end_date"] = key.strftime(settings.API_DATE_FORMAT)
        else:
            the_data = key.strftime(settings.API_DATE_FORMAT)
            outList.append({"start_date": the_data,
                            "end_date": the_data,
                            "members": out[key]})

    return JsonResponse(outList, safe=False)


def getMembersOfPGRanges(request, org_id, date_=None):
    """
    Vrne seznam objektov, ki vsebujejo poslance v poslanski skupini.
    Vsak objekt ima start_time, end_time in id-je poslancev. Objektov je
    toliko, kot je sprememb članstev v poslanski skupini. Vsak dan, ko poslanska
    skupina dobi, izgubi, ali zamenja člana zgeneriramo nov objekt.
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    tempDate = settings.MANDATE_START_TIME.date()
    members = Membership.objects.filter(organization__id=org_id)
    out = {(tempDate+timedelta(days=days)): {int(org_id): []}
           for days
           in range((fdate-tempDate).days+1)}

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
        for days in range((end_time-start_time).days + 1):
            day = out[(start_time+timedelta(days=days))]
            day[member.organization.id].append(member.person.id)

    keys = out.keys()
    keys.sort()
    outList = [{"start_date": keys[0].strftime(settings.API_DATE_FORMAT),
                "end_date":keys[0].strftime(settings.API_DATE_FORMAT),
                "members":out[keys[0]][int(org_id)]}]
    for key in keys:
        if out[key][int(org_id)] == outList[-1]["members"]:
            outList[-1]["end_date"] = key.strftime(settings.API_DATE_FORMAT)
        else:
            the_date = key.strftime(settings.API_DATE_FORMAT)
            outList.append({"start_date": the_date,
                            "end_date": the_date,
                            "members": out[key][int(org_id)]})

    return JsonResponse(outList, safe=False)


def getMembershipsOfMember(request, person_id, date=None):
    """Returns all memberships of specific MP."""

    if date:
        fdate = datetime.strptime(date, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    memberships = Membership.objects.filter(Q(start_time__lte=fdate) |
                                            Q(start_time=None),
                                            Q(end_time__gte=fdate) |
                                            Q(end_time=None),
                                            person__id=person_id)

    out_init_dict = {org_type: []
                     for org_type
                     in set([member.organization.classification
                            for member
                            in memberships]
                            )
                     }

    for mem in memberships:
        links = mem.organization.links.filter(note__in=['spletno mesto DZ',
                                                        'DZ page url'])
        if links:
            url = links.first().url
        else:
            url = None
        classification = out_init_dict[mem.organization.classification]
        classification.append({'org_type': mem.organization.classification,
                               'org_id': mem.organization.id,
                               'name': mem.organization.name,
                               'url': url})
    return JsonResponse(out_init_dict)


def getAllTimeMemberships(request):
    """Returns all memberships of all MPs."""

    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(organization__in=parliamentary_group)
    return JsonResponse([{"start_time": member.start_time,
                          "end_time": member.end_time,
                          "id": member.person.id} for member in members],
                        safe=False)


def getAllTimeMPs(request, date_=None):
    """Returns all memberhips for all MPs."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().today()

    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        organization__in=parliamentary_group)

    return JsonResponse([{'id': i.person.id,
                          'name': i.person.name,
                          'membership': i.organization.name,
                          'acronym': i.organization.acronym,
                          'classification': i.person.classification,
                          'family_name': i.person.family_name,
                          'given_name': i.person.given_name,
                          'additional_name': i.additional_name,
                          'honorific_prefix': i.honorific_prefix,
                          'honorific_suffix': i.honorific_suffix,
                          'patronymic_name': i.patronymic_name,
                          'sort_name': i.sort_name,
                          'email': i.email,
                          'gender': i.gender,
                          'birth_date': str(i.birth_date),
                          'death_date': str(i.death_date),
                          'summary': i.summary,
                          'biography': i.biography,
                          'image': i.image,
                          'district': '',
                          'gov_url': i.gov_url.url,
                          'gov_id': i.gov_id,
                          'gov_picture_url': i.gov_picture_url,
                          'voters': i.voters,
                          'active': i.active,
                          'party_id': i[0].organization.id} for i in members], safe=False)


def getOrganizatonByClassification(request):
    """Returns organizations by classification(working bodies, PG, council)."""

    workingBodies = Organization.objects.filter(classification__in=["odbor", "komisija", "preiskovalna komisija"])
    parliamentaryGroups = Organization.objects.filter(classification__in=PS_NP)
    council = Organization.objects.filter(classification="kolegij")

    return JsonResponse({"working_bodies": [{"id": wb.id,
                                             "name": wb.name} for wb in workingBodies],
                         "parliamentary_groups": [{"id": pg.id,
                                                   "name": pg.name} for pg in parliamentaryGroups],
                         "council": [{"id": c.id,
                                      "name": c.name} for c in council]})


def getOrganizationRolesAndMembers(request, org_id, date_=None):
    """
    Returns all roles of Organization. This doesn't work with PGs.
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().today()
    org = Organization.objects.filter(id=org_id)
    out = {}
    trans_map = {"debug": "debug",
                 "predsednik": "president",
                 "predsednica": "president",
                 smart_str("član"): "members",
                 smart_str("namestnica člana"): "viceMember",
                 smart_str("namestnik člana"): "viceMember",
                 smart_str("članica"): "members",
                 "podpredsednica": "vice_president",
                 "podpredsednik": "vice_president"}
    if org:
        out = {"debug": [],
               "members": [],
               "president": [],
               "vice_president": [],
               "viceMember": []}
        out["name"] = org[0].name
        memberships = Membership.objects.filter(Q(start_time__lte=fdate) |
                                                Q(start_time=None),
                                                Q(end_time__gte=fdate) |
                                                Q(end_time=None),
                                                organization_id=org_id)

        for member in memberships:
            post = member.memberships.filter(Q(start_time__lte=fdate) |
                                             Q(start_time=None),
                                             Q(end_time__gte=fdate) |
                                             Q(end_time=None))
            if post:
                role = out[trans_map[smart_str(post[0].role)]]
                role.append(member.person.id)
            else:
                out[trans_map[smart_str("debug")]].append(member.person.id)
        out["members"] += out["debug"]
    return JsonResponse(out)


def getTags(request):
    """Returns all tags."""

    out = [{"name": tag.name,
            "id": tag.id} for tag in Tag.objects.all().exclude(id__in=[1, 2, 3, 4, 5, 8, 9])]

    return JsonResponse(out, safe=False)


def getDistricts(request):
    """Returns all districts."""

    out = [{"id": area.id,
            "name": area.name} for area in Area.objects.filter(calssification="okraj")]

    return JsonResponse(out, safe=False)


def getSpeechData(request, speech_id):
    """Returns data of specific speech."""

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
    """Returns result of motion/vote."""

    output = {"result": Motion.objects.get(id=motion_id).result}

    return JsonResponse(output, safe=False)


def getPersonData(request, person_id):
    """Returns data of specific person.
       Method is used for data enrichment in parlalize.
    """

    person = Person.objects.filter(id=person_id)
    if person:
        obj = {'name': person[0].name,
               'gender': person[0].gender if person[0].gender else 'unknown',
               'gov_id': person[0].gov_id,
               }
    else:
        obj = {}
    return JsonResponse(obj)


def isSpeechOnDay(request, date_=None):
    """Returns True if at least one speech happened on a specific day."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    edate = fdate + timedelta(hours=23, minutes=59)
    speech = Speech.objects.filter(start_time__gte=fdate,
                                   start_time__lte=(edate))
    return JsonResponse({"isSpeech": True if speech else False})


def isVoteOnDay(request, date_=None):
    """Returns True if vote happend on a specific day."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    print fdate
    edate = fdate + timedelta(hours=23, minutes=59)
    votes = Vote.objects.filter(start_time__gte=fdate,
                                start_time__lte=(edate))

    return JsonResponse({"isVote": True if votes else False})


def getSpeechesIDs(request, person_id, date_=None):
    """Returns all speech ids of MP."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    fdate = fdate.replace(hour=23, minute=59)
    speaker = get_object_or_404(Person, id=person_id)
    speeches_queryset = Speech.getValidSpeeches(fdate)
    speeches_queryset = speeches_queryset.filter(speaker=speaker,
                                                 start_time__lte=fdate)
    speeches_ids = list(speeches_queryset.values_list("id", flat=True))
    return JsonResponse(speeches_ids, safe=False)


def getPGsSpeechesIDs(request, org_id, date_=None):
    """Returns speechs ids of specifig PG."""

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    fdate = fdate.replace(hour=23, minute=59)
    ranges = json.loads(getMembersOfPGRanges(request, org_id, date_).content)

    speeches_ids = []
    speeches_queryset = Speech.getValidSpeeches(fdate)
    for ran in ranges:
        start = datetime.strptime(ran["start_date"], settings.API_DATE_FORMAT)
        start = start.replace(hour=23, minute=59)
        end = datetime.strptime(ran["end_date"], settings.API_DATE_FORMAT)
        end = end.replace(hour=23, minute=59)
        for member in ran["members"]:

            speeches = speeches_queryset.filter(speaker__id=member,
                                                start_time__lte=end,
                                                start_time__gte=start)
            speeches_ids += list(speeches.values_list("id", flat=True))
    return JsonResponse(speeches_ids, safe=False)


def getMembersWithFuction(request):
    """
    TODO fix spelling
    * @api {get} getMembersWithFuction/ MPs with functions in DZ
    * @apiName getMembersWithFuction
    * @apiGroup MPs
    * @apiDescription This function returns all MPs that have a function in DZ.
      That means president or vice president of the national council.

    * @apiSuccess {Integer[]} members_with_function Parladata ids of MPs with functions in DZ.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersWithFuction/
    
    * @apiSuccessExample {json} Example response:
    {
        "members_with_function": [
            29,
            11,
            62
        ]
    }
    """
    
    fdate = datetime.today()
    data = []
    dz = Organization.objects.filter(id=DZ_ID)
    members = Membership.objects.filter(Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        organization__in=dz)
    for member in members:
        for post in member.memberships.all():
            if post.role in ["predsednik", "podpredsednik"]:
                data.append(member.person.id)

    return JsonResponse({"members_with_function": data}, safe=False)


def getDocumentOfMotion(request, motion_id):
    """
    Returns all documents of specific motion/vote
    """

    if Link.objects.filter(motion=motion_id):
        link = str(Link.objects.filter(motion=motion_id)[0]).split('/')
        true_link = str('https://cdn.parlameter.si/v1/dokumenti/' + link[4])
        return JsonResponse({"link": true_link}, safe=False)
    else:
        return JsonResponse({"link": None}, safe=False)


def getAllQuestions(request, date_=None):
    """
    Returns array of all questions. Objects have only link with note Besedilo.
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    question_queryset = Question.objects.filter(date__lte=fdate)

    data = []

    for question in question_queryset:
        link = question.links.filter(note__icontains="Besedilo")
        if link:
            link = link[0].url
        else:
            link = None
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': getIdSafe(question.recipient_person),
                 'recipient_org_id': getIdSafe(question.recipient_organization),
                 'recipient_text': question.recipient_text,
                 'link': link,
                 }
        data.append(q_obj)

    return JsonResponse(data, safe=False)


def getBallotsCounter(voter_obj, date_=None):
    """
    Returns monthly ballots count of voter/voter_org
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    fdate = fdate + timedelta(days=1)

    data = []

    if type(voter_obj) == Person:
        ballots = Ballot.objects.filter(voter=voter_obj,
                                        vote__start_time__lt=fdate)
    elif type(voter_obj) == Organization:
        ballots = Ballot.objects.filter(voterparty=voter_obj,
                                        vote__start_time__lt=fdate)

    ballots = ballots.annotate(month=DateTime("vote__start_time",
                                              "month",
                               tzinfo=None)).values("month").values('option',
                                                                    'month')
    ballots = ballots.annotate(ballot_count=Count('option')).order_by('month')

    votes = Vote.objects.filter(start_time__lt=fdate)
    votes = votes.annotate(month=DateTime("start_time",
                                          "month",
                           tzinfo=None)).values("month")
    votes = votes.annotate(total_votes=Count('id')).order_by("month")

    for month in votes:
        date_ = month['month']
        total = month['total_votes']

        temp_data = {'date': date_.strftime(settings.API_DATE_FORMAT),
                     'date_ts': date_,
                     'ni': 0,
                     'kvorum': 0,
                     'za': 0,
                     'proti': 0,
                     'total': total
                     }

        sums_of_month = ballots.filter(month=date_)
        for sums in sums_of_month:
            temp_data[sums['option']] = sums['ballot_count']

        data.append(temp_data)

    return data


def getBallotsCounterOfPerson(request, person_id, date_=None):
    """
    Api endpoint which returns ballots count of voter
    """
    person = Person.objects.get(id=person_id)
    data = getBallotsCounter(person, date_=None)
    return JsonResponse(data, safe=False)


def getBallotsCounterOfParty(request, party_id, date_=None):
    """
    Api endpoint which returns ballots count of party
    """
    party = Organization.objects.get(id=party_id)
    data = getBallotsCounter(party, date_=None)
    return JsonResponse(data, safe=False)


@csrf_exempt
def addQuestion(request):
    """
    This is an api endpoint function that saves a new question when prompted with a POST request.

    JSON data model:
    {
        "ps": "Poslanska skupina Slovenske demokratske stranke",
        "links": [{
            "date": "30.12.2016",
            "url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/PoslankeInPoslanci/poslanec?idOseba=P268",
            "name": "Dopis za posredovanje pisnega vprašanja - PPDZ"
        }, {
            "date": "29.12.2016",
            "url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/PoslankeInPoslanci/poslanec?idOseba=P268",
            "name": "Besedilo"
        }],
        "datum": "29.12.2016",
        "naslovljenec": "minister za infrastrukturo",
        "naslov": "v zvezi z nepravilnostmi pri pomoči na slovenskih cestah",
        "vlagatelj": "Lep Šimenko Suzana"
    }

    TODO:
    - determinePerson2() is a non-MVP function that determines the person based on
      their post at the ministry. Requires extra data to be entered manually.
    - determineOrganization() is a non-MVP function that determines the Organization
      the question was directed to. Requires extra data to be entered manually.
    """
    print request.method
    if request.method == 'POST':
        rep = {" mag. ": " ", " mag ": " ", " dr. ": " ", " dr ": " "}
        data = json.loads(request.body)
        session = determineSession(data['datum'])
        name = replace_all(data['vlagatelj'], rep)
        person = determinePerson(name)
        dz = Organization.objects.get(id=DZ_ID)

        if Question.objects.filter(session=session,# TODO use data['datum']
                                   title=data['naslov'],
                                   date=datetime.strptime(data['datum'], '%d.%m.%Y'),
                                   author=person, # TODO use data['vlagatelj']
                                   # recipient_person=determinePerson2(), # TODO use data['naslovljenec'], not MVP
                                   # recipient_organization=determineOrganization(), # TODO use data['naslovljenec'], not MVP
                                   recipient_text=data['naslovljenec']
                                   ):
            return JsonResponse({'status': 'This question is allready saved'})

        question = Question(session=session,# TODO use data['datum']
                            date=datetime.strptime(data['datum'], '%d.%m.%Y'),
                            title=data['naslov'],
                            author=person, # TODO use data['vlagatelj']
                            # recipient_person=determinePerson2(), # TODO use data['naslovljenec'], not MVP
                            # recipient_organization=determineOrganization(), # TODO use data['naslovljenec'], not MVP
                            recipient_text=data['naslovljenec'],
                            json_data=request.body
                            )
        question.save()

        print 'save question'

        for link in data['links']:
            link = Link(url=link['url'],
                        note=link['name'],
                        date=datetime.strptime(link['date'], '%d.%m.%Y'),
                        session=session, # TODO use data['datum']
                        organization=dz,
                        question=question).save()
            print 'save link'
            # TODO: link needs tags, but tags need to be determined first

        return JsonResponse({'saved': True,
                             'status': 'AllIsWell',
                             'found_session': True if session else False,
                             'found_person': True if person else False,
                             })
    else:
        return JsonResponse({'status': 'request must be post'})

        return JsonResponse({"link": None}, safe=False)


def getAllChangesAfter(request,
                       person_update_time,
                       session_update_time,
                       speech_update_time,
                       ballots_update_time,
                       question_update_time):
    """
    This is an api endpoint function that uses for fast update of parlalize.
    Returns all session, person, speeches, ballots and questions updated
    after {datetime_}
    """
    time_of_person = datetime.strptime(person_update_time,
                                       settings.API_DATE_FORMAT + "_%H:%M")

    time_of_session = datetime.strptime(session_update_time,
                                        settings.API_DATE_FORMAT + "_%H:%M")

    time_of_speech = datetime.strptime(speech_update_time,
                                       settings.API_DATE_FORMAT + "_%H:%M")

    time_of_ballot = datetime.strptime(ballots_update_time,
                                       settings.API_DATE_FORMAT + "_%H:%M")

    time_of_question = datetime.strptime(question_update_time,
                                         settings.API_DATE_FORMAT + "_%H:%M")

    par_group = Organization.objects.all()
    par_group = par_group.filter(classification__in=PS_NP)
    data = {}

    print "sessions"
    data['sessions'] = []
    sessions = Session.objects.filter(updated_at__gte=time_of_session)
    for i in sessions.order_by('-start_time'):
        organizations = i.organizations.all().values_list("id", flat=True)
        data["sessions"].append({'mandate': i.mandate,
                                 'name': i.name,
                                 'gov_id': i.gov_id,
                                 'start_time': i.start_time,
                                 'end_time': i.end_time,
                                 'organizations_id': map(str, organizations),
                                 'organization_id': i.organization.id,
                                 'classification': i.classification,
                                 'id': i.id,
                                 'is_in_review': i.in_review})

    print "persons"
    data['persons'] = []
    persons = Person.objects.filter(updated_at__gte=time_of_person)
    for i in persons:
        pg = i.memberships.filter(organization=par_group)
        data["persons"].append({'id': i.id,
                                'name': i.name,
                                'membership': pg[0] if pg else None,
                                'classification': i.classification,
                                'family_name': i.family_name,
                                'given_name': i.given_name,
                                'additional_name': i.additional_name,
                                'honorific_prefix': i.honorific_prefix,
                                'honorific_suffix': i.honorific_suffix,
                                'patronymic_name': i.patronymic_name,
                                'sort_name': i.sort_name,
                                'email': i.email,
                                'gender': i.gender,
                                'birth_date': str(i.birth_date),
                                'death_date': str(i.death_date),
                                'summary': i.summary,
                                'biography': i.biography,
                                'image': i.image,
                                'district': '',
                                'gov_id': i.gov_id,
                                'gov_picture_url': i.gov_picture_url,
                                'voters': i.voters,
                                'active': i.active})

    print "speeches"
    speeches = Speech.objects.filter(Q(updated_at__gte=time_of_speech) |
                                     Q(created_at__gte=time_of_speech))
    print speeches.count()
    data['speeches'] = [model_to_dict(speech, fields=[field.name
                                                      for field
                                                      in speech._meta.fields])
                        for speech in speeches]

    print "ballots"
    ballots = Ballot.objects.filter(updated_at__gte=time_of_ballot)
    print ballots.count()
    data['ballots'] = [model_to_dict(ballot,
                                     fields=['id',
                                             'vote',
                                             'voter',
                                             'option']) for ballot in ballots]
    newVotes = list(set(list(ballots.values_list("vote__session__id",
                                                 flat=True))))
    data['sessions_of_updated_votes'] = newVotes

    print "questions"
    data['questions'] = []

    question_queryset = Question.objects.filter(updated_at__gte=time_of_question)

    for question in question_queryset:
        link = question.links.filter(note__icontains="Besedilo")
        if link:
            link = link[0].url
        else:
            link = None
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': getIdSafe(question.recipient_person),
                 'recipient_org_id': getIdSafe(question.recipient_organization),
                 'recipient_text': question.recipient_text,
                 'link': link,
                 }
        data['questions'].append(q_obj)

    return JsonResponse(data)


def monitorMe(request):
    """Checks if API is working."""

    r = requests.get('https://data.parlameter.si/v1/getMPs')
    if r.status_code == 200:
        return HttpResponse('All iz well.')
    else:
        return HttpResponse('PANIC!')
