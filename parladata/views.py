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
    * @api {get} /getMPs/:date Request information of all members
    * @apiName GetMembers
    * @apiGroup Members
    *
    * @apiParam {date} date is optional parameter and
    *return members on this day.
    *
    * @apiSuccess {Json} return arrayo f all members. Each elemnt is object of
    * member data.
    * @apiSuccess {String} lastname  Lastname of the User.
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


def getIDsOfAllMinisters(request, date_=None):
    """
    TODO: write doc
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    ministry = Organization.objects.filter(classification__in=['ministrstvo',
                                                               'vlada'])
    memberships = Membership.objects.filter(Q(start_time__lte=fdate) |
                                            Q(start_time=None),
                                            Q(end_time__gte=fdate) |
                                            Q(end_time=None),
                                            organization__in=ministry)
    ids = list(set(list(memberships.values_list('person_id', flat=True))))

    return JsonResponse({'ministers_ids': ids}, safe=False)


def getMinistrStatic(request, person_id, date_=None):
    """
    TODO: write doc
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = dict()
    ministry = Organization.objects.filter(classification__in=['ministrstvo',
                                                              'vlada'])
    person = get_object_or_404(Person, id=person_id)
    memberships = person.memberships.filter(Q(start_time__lte=fdate) |
                                            Q(start_time=None),
                                            Q(end_time__gte=fdate) |
                                            Q(end_time=None))

    ministry = memberships.filter(organization__classification__in=['ministrstvo',
                                                                 'vlada'])
    if len(ministry) > 1:
        ministry = ministry.filter(organization__classification='ministrstvo')
    ministry_data = {'name': ministry[0].organization.name,
                     'id': ministry[0].organization.id,
                     'acronym': ministry[0].organization.acronym}

    party = memberships.filter(organization__classification__in=PS_NP)
    if party:
        party_data = {'name': party[0].organization.name,
                      'id': party[0].organization.id,
                      'acronym': party[0].organization.acronym}
    else:
        party_data = {}

    PS_NP_VLADA = ['ministrstvo', 'vlada'] + PS_NP
    groups = memberships.exclude(organization__classification__in=PS_NP_VLADA)

    groups_data = [{'name': membership.organization.name,
                    'id': membership.organization.id,
                    'acronym': membership.organization.acronym}
                   for membership
                   in groups]

    # calcutaes age of MP
    try:
        birth_date = str(person.birth_date)
        age = date.today() - date(int(birth_date[:4]),
                                  int(birth_date[5:7]),
                                  int(birth_date[8:10]))
        age = age.days / 365
    except:
        client.captureException()
        age = None

    twitter = person.link_set.filter(tags__name__in=['tw'])
    facebook = person.link_set.filter(tags__name__in=['fb'])
    linkedin = person.link_set.filter(tags__name__in=['linkedin'])

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

    district = list(person.districts.all().values_list('id',
                                                       flat=True))
    if not district:
        district = None

    data = {
        'previous_occupation': person.previous_occupation,
        'education': person.education,
        'party': party_data,
        'district': district,
        'age': age,
        'groups': groups_data,
        'name': person.name,
        'social': social_output,
        'gov_id': person.gov_id,
        'gender': 'm' if person.gender == 'male' else 'f',
        'ministry': ministry_data,
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
                     'organization_id': i.organization_id,
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
    speeches_queryset = Speech.getValidSpeeches(tdate)
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
    """Returns number of MP attended sessions."""

    data = {}
    allBallots = Ballot.objects.filter(option='za')
    for i in getMPObjects():
        data[i.id] = len(list(set(allBallots.filter(voter=i.id).values_list('vote__session', flat=True))))

    return JsonResponse(data[int(person_id)], safe=False)


def getNumberOfAllMPAttendedSessions(request, date_):
    """Return number of attended Sessions for all MPs."""

    fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date() + timedelta(days=1) - timedelta(minutes=1)
    data = {"sessions": {}, "votes": {}}
    for member in getMPObjects(fdate):
        # list of all sessions of MP
        allOfHimS = list(set(Ballot.objects.filter(voter__id=member.id,
                                                   vote__start_time__lte=fdate).values_list("vote__session", flat=True)))
        # list of all session that the opiton of ballto was: kvorum, proti, za
        votesOnS = list(set(Ballot.objects.filter(Q(option="kvorum") |
                                                  Q(option="proti") |
                                                  Q(option="za"),
                                                  voter__id=member.id,
                                                  vote__start_time__lte=fdate).values_list("vote__session", flat=True)))
        # list of all votes of MP
        allOfHimV = list(set(Ballot.objects.filter(voter__id=member.id,
                                                   vote__start_time__lte=fdate).values_list("vote", flat=True)))
        # list of all votes that the opiton of ballto was: kvorum, proti, za
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
    """Returns all speeches of MPs¸"""

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
    """Returns all speecehs of all MPs."""

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
                if motion.result == '0':
                    result = False
                elif motion.result == '1':
                    result = True
                else:
                    result = None
                links = motion.links.all()
                links_list = [{'name': link.name, 'url': link.url}
                              for link in links]
                data.append({'id': motion.id,
                             'vote_id': vote.id,
                             'text': motion.text,
                             'result': result,
                             'tags': map(smart_str, vote.tags.names()),
                             'doc_url': links_list,
                             'start_time': vote.start_time})
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

    data = []
    for i in members:
        p = i.person
        districts = ''

        if p.districts:
            districts = p.districts.all().values_list("name", flat=True)
            districts = [smart_str(dist) for dist in districts]
            if not districts:
                districts = None
        else:
            districts = None

        data.append({'id': p.id,
                     'name': p.name,
                     'membership': i.organization.name,
                     'acronym': i.organization.acronym,
                     'classification': p.classification,
                     'family_name': p.family_name,
                     'given_name': p.given_name,
                     'additional_name': p.additional_name,
                     'honorific_prefix': p.honorific_prefix,
                     'honorific_suffix': p.honorific_suffix,
                     'patronymic_name': p.patronymic_name,
                     'sort_name': p.sort_name,
                     'email': p.email,
                     'birth_date': str(p.birth_date),
                     'death_date': str(p.death_date),
                     'summary': p.summary,
                     'biography': p.biography,
                     'image': p.image,
                     'district': districts,
                     'gov_url': p.gov_url.url,
                     'gov_id': p.gov_id,
                     'gov_picture_url': p.gov_picture_url,
                     'voters': p.voters,
                     'active': p.active,
                     'party_id': i.organization.id})
    return JsonResponse(data, safe=False)


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
    Returns ids of all members with function in DZ.
    (president and vice president)
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
        recipient_person = question.recipient_person.all().values_list('id',
                                                                       flat=True)
        recipient_org = question.recipient_organization.all().values_list('id',
                                                                          flat=True)
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': list(recipient_person),
                 'recipient_org_id': list(recipient_org),
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
        print data
        session = determineSession(data['datum'])
        name = replace_all(data['vlagatelj'], rep)
        authorPerson = determinePerson(name)
        dz = Organization.objects.get(id=DZ_ID)
        date_of = datetime.strptime(data['datum'], '%d.%m.%Y')
        recipients = parseRecipient(data['naslovljenec'], date_of)
        recipient_persons = [person['recipient']
                             for person
                             in recipients
                             if person['type'] == 'person']
        recipient_organizations = [person['recipient']
                                   for person
                                   in recipients
                                   if person['type'] == 'org']
        print session, data['naslov'], datetime.strptime(data['datum'], '%d.%m.%Y'), person, data['naslovljenec']
        if Question.objects.filter(session=session,# TODO use data['datum']
                                   title=data['naslov'],
                                   date=datetime.strptime(data['datum'], '%d.%m.%Y'),
                                   author=authorPerson, # TODO use data['vlagatelj']
                                   #recipient_person=determinePerson2(), # TODO use data['naslovljenec'], not MVP
                                   # recipient_organization=determineOrganization(), # TODO use data['naslovljenec'], not MVP
                                   recipient_text=data['naslovljenec']
                                   ):
            return JsonResponse({'status': 'This question is allready saved'})

        question = Question(session=session,
                            date=datetime.strptime(data['datum'], '%d.%m.%Y'),
                            title=data['naslov'],
                            author=authorPerson,
                            recipient_text=data['naslovljenec'],
                            json_data=request.body
                            )
        question.save()
        question.recipient_person.add(*recipient_persons)
        question.recipient_organization.add(*recipient_organizations)

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

    # delete motions without text before each update of parlalize
    deleteMotionsWithoutText()

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
    newVotesSessions = list(set(list(ballots.values_list("vote__session__id",
                                                         flat=True))))
    newVotes = list(set(list(ballots.values_list("vote_id",
                                                 flat=True))))
    data['sessions_of_updated_votes'] = newVotesSessions

    print "questions"
    data['questions'] = []

    question_queryset = Question.objects.filter(updated_at__gte=time_of_question)

    for question in question_queryset:
        link = question.links.filter(note__icontains="Besedilo")
        if link:
            link = link[0].url
        else:
            link = None
        recipient_person = question.recipient_person.all().values_list('id',
                                                                       flat=True)
        recipient_org = question.recipient_organization.all().values_list('id', 
                                                                          flat=True)
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': list(recipient_person),
                 'recipient_org_id': list(recipient_org),
                 'recipient_text': question.recipient_text,
                 'link': link,
                 }
        data['questions'].append(q_obj)

    ballots = Ballot.objects.filter(created_at__gte=time_of_ballot)
    newVotes = list(set(list(ballots.values_list("vote_id",
                                                 flat=True))))
    # build mail for new votes
    if newVotes:
        sendMailForEditVotes({vote.id: vote.session_id
                              for vote
                              in Vote.objects.filter(id__in=newVotes)
                              }
                             )

    return JsonResponse(data)


def monitorMe(request):
    """Checks if API is working."""

    r = requests.get('https://data.parlameter.si/v1/getMPs')
    if r.status_code == 200:
        return HttpResponse('All iz well.')
    else:
        return HttpResponse('PANIC!')


def getVotesTable(request, date_to=None):
    """
    Pandas table
    """

    if date_to:
        fdate = datetime.strptime(date_to,
                                  settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    for session in Session.objects.all():
        votes = Vote.objects.filter(session=session,
                                    start_time__lte=fdate)
        for vote in votes:
            motion = vote.motion
            for ballot in Ballot.objects.filter(vote=vote):
                data.append({'id': ballot.id,
                             'voter': ballot.voter_id,
                             'option': ballot.option,
                             'voterparty': ballot.voterparty_id,
                             'orgvoter': ballot.orgvoter_id,
                             'result': False if motion.result == '0' else True,
                             'text': motion.text,
                             'date': vote.start_time,
                             'vote_id': vote.id,
                             'session_id': session.id})

    return JsonResponse(data, safe=False)


def getVotesOfSessionTable(request, session_id, date_to=None):
    """
    Pandas table
    """

    if date_to:
        fdate = datetime.strptime(date_to,
                                  settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    session = get_object_or_404(Session, id=session_id)
    votes = Vote.objects.filter(session=session,
                                start_time__lte=fdate)
    for vote in votes:
        motion = vote.motion
        for ballot in Ballot.objects.filter(vote=vote):
            data.append({'id': ballot.id,
                         'voter': ballot.voter_id,
                         'option': ballot.option,
                         'voterparty': ballot.voterparty_id,
                         'orgvoter': ballot.orgvoter_id,
                         'result': False if motion.result == '0' else True,
                         'text': motion.text,
                         'date': vote.start_time,
                         'vote_id': vote.id,
                         'session_id': session.id})

    return JsonResponse(data, safe=False)


def getVotesTableExtended(request, date_to=None):
    """
    Pandas table
    """
    orgs = {}
    for org in Organization.objects.filter(classification__in=PS_NP):
        orgs[org.id] = org.acronym

    if date_to:
        fdate = datetime.strptime(date_to,
                                  settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []
    for session in Session.objects.all():
        votes = Vote.objects.filter(session=session,
                                    start_time__lte=fdate)
        for vote in votes:
            tags = [tag.name for tag in vote.tags.all()]
            motion = vote.motion
            for ballot in Ballot.objects.filter(vote=vote):
                data.append({'id': ballot.id,
                             'voter': ballot.voter_id,
                             'option': ballot.option,
                             'voterparty': ballot.voterparty_id,
                             'orgvoter': ballot.orgvoter_id,
                             'result': False if motion.result == '0' else True,
                             'text': motion.text,
                             'date': vote.start_time,
                             'vote_id': vote.id,
                             'session_id': session.id,
                             'tags': ','.join(tags)})

    return JsonResponse(data, safe=False)


def getAllAllSpeeches(request):
    """
    return non valid speeches too
    """
    data = []
    speeches_queryset = Speech.objects.all()
    speeches = speeches_queryset.filter()
    for speech in speeches:
        data.append(model_to_dict(speech,
                                  fields=[field.name for field in speech._meta.fields],
                                  exclude=[]))

    return JsonResponse(data, safe=False)
