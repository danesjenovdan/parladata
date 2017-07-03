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
                     'email': '',
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


def getIDsOfAllMinisters(request, date_=None):
    """
    TODO: write doc
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    ministry = Organization.objects.filter(classification__in=['ministrstvo',
                                                               'vlada',
                                                               'sluzba vlade',
                                                               'urad vlade'])
    memberships = Membership.objects.filter(organization__in=ministry)
    ids = list(set(list(memberships.values_list('person_id', flat=True))))

    return JsonResponse({'ministers_ids': ids}, safe=False)


def getMinistrStatic(request, person_id, date_=None):
    """
    Returns all government memberships of person
    TODO: write doc
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()
    data = []

    person = get_object_or_404(Person, id=person_id)
    """memberships = person.memberships.filter(Q(start_time__lte=fdate) |
                                            Q(start_time=None),
                                            Q(end_time__gte=fdate) |
                                            Q(end_time=None))"""
    memberships = person.memberships.all()

    ministry = memberships.filter(organization__classification__in=['ministrstvo',
                                                                    'vlada',
                                                                    'sluzba vlade',
                                                                    'urad vlade'])
    for ministr in ministry:
        ministry_data = {'name': ministr.organization.name,
                         'id': ministr.organization.id,
                         'acronym': ministr.organization.acronym}

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
            #client.captureException()
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

        data.append({
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
            'start_time': ministr.start_time
        })
    return JsonResponse(data, safe=False)


def getSessions(request, date_=None):
    """
    * @api {get} getSessions/{?date} List all sessions
    * @apiName getSessions
    * @apiGroup Sessions
    * @apiDescription This function returns an array of objects listing
      all sessions that have happened since the beggining of the current mandate.
      The optional date parameter determines the date up until which sessions should
      be returned. If no date is specified it is assumed the date is today.
    * @apiParam {date} date Optional date.

    * @apiSucess {Object[]} / An array of objects, each object representing a session.
    * @apiSuccess {String} /.classification Session classification. Returns null if the session
      doesn't have classification. Sometimes used for internal sorting purposes.
    * @apiSuccess {Boolean} /.is_in_review Return true if the session is in review, returns false otherwise.
    * @apiSuccess {String} /.name Session name.
    * @apiSuccess {String} /.gov_id Session id on http://www.dz-rs.si. Not technically an ID, more of an URI,
      but it is still used to match the session to the government's website.
    * @apiSuccess {String} /.mandate Currently return null, but functions as a placeholder to determine
      the mandate the session belongs to.
    * @apiSuccess {String} /.start_time Timestamp of the session's start.
    * @apiSuccess {String[]} /.organizations_id An array of strings representing Parladata ids of organizations
      this session belongs to.
    * @apiSuccess {Integer} /.id The session's Parladata id.
    * @apiSuccess {String} /.end_time Placeholder for session's end time. Currently returns null because we don't
      know when exactly the session ends.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSessions/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getSessions/21.12.2016

    * @apiSuccessExample {json} Example response:
    [{
        "classification": null,
        "is_in_review": false,
        "name": "71. nujna seja",
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSejaDt?mandat=VII&amp;seja=14%20071.%20Nujna&amp;uid=B5BC47C4DF4749B3C12580C60036936E",
        "mandate": null,
        "start_time": "2017-02-15T01:00:00",
        "organizations_id": [],
        "id": 9179,
        "end_time": null
        }, {
        "classification": null,
        "is_in_review": false,
        "name": "27. redna seja",
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSeja?mandat=VII&amp;seja=27.%20Redna&amp;uid=1B788DD37B254072C125807900377C52",
        "mandate": null,
        "start_time": "2017-02-13T01:00:00",
        "organizations_id": ["95"],
        "id": 9158,
        "end_time": null
        }, {
        "classification": null,
        "is_in_review": false,
        "name": "47. nujna seja",
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSejaDt?mandat=VII&amp;seja=12%20047.%20Nujna&amp;uid=B93F45394862FB17C12580BF003F8548",
        "mandate": null,
        "start_time": "2017-02-13T01:00:00",
        "organizations_id": ["19"],
        "id": 9159,
        "end_time": null
    }]
    """

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
    """
    * @api {get} getSessionsOfOrg/{id}/{?date} List all sessions of a specific organization
    * @apiName getSessionsOfOrg
    * @apiGroup Sessions
    * @apiDescription This function returns an array of objects listing
      all sessions that have happened since the beggining of the current mandate in
      the specified organization. The optional date parameter determines the date up
      until which sessions should be returned. If no date is specified it is assumed
      the date is today.
    * @apiParam {id} id Organization id.
    * @apiParam {date} date Optional date.

    * @apiSucess {Object[]} / An array of objects, each object representing a session.
    * @apiSuccess {String} /.name Session name.
    * @apiSuccess {String} /.classification Session classification. Returns null if the session
      doesn't have classification. Sometimes used for internal sorting purposes.
    * @apiSuccess {String} /.start_time Timestamp of the session's start.
    * @apiSuccess {String} /.end_time Placeholder for session's end time. Currently returns null because we don't
      know when exactly the session ends.
    * @apiSuccess {String} /.mandate Currently return null, but functions as a placeholder to determine
      the mandate the session belongs to.
    * @apiSuccess {Integer} /.id The session's Parladata id.
    * @apiSuccess {String} /.gov_id Session id on http://www.dz-rs.si. Not technically an ID, more of an URI,
      but it is still used to match the session to the government's website.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSessionsOfOrg/95
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getSessionsOfOrg/95/21.12.2016

    * @apiSuccessExample {json} Example response:
    [{
        "name": "26. izredna seja",
        "classification": null,
        "start_time": "2015-12-09T01:00:00",
        "end_time": null,
        "mandate": null,
        "id": 5595,
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSeja?mandat=VII&amp;seja=26.%20Izredna&amp;uid=3B664ACC0A79164EC1257F11003317C8"
        }, {
        "name": "25. izredna seja",
        "classification": null,
        "start_time": "2015-12-01T01:00:00",
        "end_time": null,
        "mandate": null,
        "id": 5596,
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSeja?mandat=VII&amp;seja=25.%20Izredna&amp;uid=5F0E4C54348C32D1C1257F0D0035ABF5"
        }, {
        "name": "24. izredna seja",
        "classification": null,
        "start_time": "2015-11-20T01:00:00",
        "end_time": null,
        "mandate": null,
        "id": 5597,
        "gov_id": "/wps/portal/Home/deloDZ/seje/izbranaSeja?mandat=VII&amp;seja=24.%20Izredna&amp;uid=52A5C4FAC552CB55C1257EF80042C358"
    }]
    """

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


def getSpeeches(request, person_id, date_=None):
    """Returns speechs of MP."""
    """
    * @api {get} getSpeeches/{id}/{?date} MP's speeches as objects
    * @apiName getSpeeches
    * @apiGroup MPs
    * @apiDescription This function returns an array of objects, each object
      contains the corresponding speech's Parladata id and it's content. Optionally
      it returns speeches up until the optionally passed date.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object[]} / An array of all speeches as objects.
    * @apiSuccess {String} /.content The speach's content.
    * @apiSuccess {Integer} /.speech_id The speach's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSpeeches/12
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getSpeeches/12/21.12.2016

    * @apiSuccessExample {json} Example response:
    [
        {
            "content": "Hvala za besedo. \nSlovenija je, vsaj po mojem mnenju, na neki to\u010dki, poudarjam, na to\u010dki, na kateri si nikakor ne moremo privo\u0161\u010diti bohotenja javnega sektorja oziroma javne uprave. Kot smo \u017ee danes sli\u0161ali v razpravi, imamo okrog 4 tiso\u010d na\u0161ih dr\u017eavljanov, ki \u017eivijo na robu socialne stiske, okrog 120 tiso\u010d je brezposelnih, in te bo tudi to pove\u010danje ministrstev kar precej obremenilo. \u0160e najbolj obremenilo v negativnem smislu pa bo to na\u0161e gospodarstvo. Moram re\u010di, da sem pri\u010dakovala, da si bo ta vlada zamislila nek koncept vitke in produktivne javne uprave. To so pri\u010dakovali tudi na\u0161i dr\u017eavljani, ki so to tudi izrazili v svoji anketi, pa kljub temu, da nismo navedli oziroma ne navajam vira ankete, ampak je bila objavljena v ponedeljek zjutraj. Predlog sprememb zakona, ki ga imamo pred seboj, je tudi brez neke vsebinske analize in brez finan\u010dne konstrukcije. Pravite, da ta reorganizacija oziroma pove\u010danje \u0161tevila ministrstev ne bo imelo finan\u010dnih posledic. Pa \u0161e kak\u0161ne finan\u010dne posledice bodo. Upam, da bomo dobili na koncu poro\u010dilo o u\u010dinkovitosti tega va\u0161ega zakona, kot smo to tudi z na\u0161o pobudo oziroma z vlo\u017eitvijo tega amandmaja zahtevali. Menim, da bi morali razmi\u0161ljati predvsem v smeri zdru\u017eevanja ministrstev in se tako nekako poenotiti oziroma poistovetiti z drugimi dr\u017eavami, kot je \u017ee bilo danes v razpravi omenjeno, primerljivimi evropskimi dr\u017eavami. \u010ce pa bi \u017ee razmi\u0161ljali o pove\u010danju \u0161tevila ministrstev, bi bilo pa verjetno dobro, da bi razmi\u0161ljali o ministrstvih, ki prina\u0161ajo neko dodano vrednost, ministrstvo za gospodarske, evropske zadeve in tako naprej. Moram pa re\u010di, da sem danes vesela, glede na to, da se v\u010deraj na odboru za notranjo politiko nih\u010de iz SMC ni oglasil, danes je pa zelo lepo, da ste se vsi razpravljavci prijavili. Hvala.",
            "speech_id": 524506
        }, {
            "content": "Hvala za besedo. Lepo pozdravljeni vsi.\nGlede na dano situacijo v kateri se nahajamo in vsi vemo, da ni prav ro\u017enata, moram re\u010di, da sem bila prepri\u010dana, da bo vlada \u0161la prav v nasprotno smer, se pravi v kr\u010denje ministrstva ne pa v \u0161iritev. Pri\u010dakovala sem tudi, da se bo zavzela za koncept vitke in produktivne javne uprave. Prav tako mislim, da so to pri\u010dakovali od te vlade tudi na\u0161i dr\u017eavljani, na\u0161i davkopla\u010devalci tako kot je rekel kolega Vinko, so se izrekli tudi na anketi, ki je bila objavljena v ponedeljek, kar nekaj \u010dez 80% so proti \u0161iritvi javne uprave. Nikakor pa se ne morem dati prepri\u010dati oziroma me ne morete prepri\u010dati, da ta predlog sprememb ne bo imel finan\u010dnih posledic, kot je zapisano. Pri\u010dakovala sem tudi neko finan\u010dno konstrukcijo. \u010ce povem za primer kako smo to delali na lokalni samoupravi. \u010ce smo \u017eeleli ustanoviti nek odbor s petimi \u010dlani, smo morali narediti temeljito finan\u010dno konstrukcijo in potem tudi \u010dez \u010das poro\u010dati o realizaciji. Prav zanimivo bi bilo videti meseca januarja, februarja, ko bodo nova ministrstva prevzela vse svoje naloge, kak\u0161na bi bila ta slika s finan\u010dnega in seveda kadrovskega podro\u010dja. Hvala.",
            "speech_id": 580777
        }
    ]
    """

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
    """Returns speeches of MP in range(from specific date to specific date)."""
    """
    * @api {get} getSpeechesInRange/{id}/{date_from}/{date_to} Get all MP's speeches between two dates
    * @apiName getSpeechesInRange
    * @apiGroup MPs
    * @apiDescription This function returns an array of objects, each object
      contains the corresponding speech's Parladata id and it's content. All the
      speeches have happened between the two dates set in the url.

    * @apiSuccess {Object[]} / An array of objects containing speech's content and Parladata id.
    * @apiSuccess {String} /.content The speach's content.
    * @apiSuccess {Integer} /.speech_id The speach's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSpeechesInRange/12/10.12.2015/1.2.2016

    * @apiSuccessExample {json} Example response:
    [{
        "content": "Hvala za besedo, predsedujo\u010di. Lep pozdrav vsem tukaj v dvorani! \nDejstvo je, da na\u0161a vlada ne vlada. To ni samo moje mnenje, to je mnenje tudi mnogih, mnogih dr\u017eavljanov. Oziroma bom rekla tako, da ko gre za sprejem nekih ukrepov, ki jih Vlada sprejema in s katerimi se \u0161e bolj praznijo \u017eepi na\u0161ih dr\u017eavljanov ali pa \u0161e bolj slabijo na\u0161e gospodarstvo, \u0161e nekako kar ob\u010dutimo delo te vlade. Ko pa gre za to, da bi naj ta vlada nekako za\u0161\u010ditila svoje dr\u017eavljane, pa vidimo, da ta vlada tega nikakor ne zmore. \nDanes smo \u017ee ve\u010dkrat sli\u0161ali, da je na\u0161a stranka pet ali \u0161estkrat zahtevala sklic seje na to temo. Seveda smo sklicali seje na to temo, ampak vse to z namenom, da nekako izvemo, kak\u0161no je mnenje, kak\u0161ni so predlogi in pa seveda tudi ukrepi te vlade. \u017dal moram re\u010di, da smo poslu\u0161ali, kot je \u017ee bilo danes tudi ugotovljeno, v bistvu samo poro\u010dila oziroma to, kaj se ne bo v Sloveniji zgodilo. Ampak moram re\u010di, glej ga vraga, vse, kar je Vlada napovedala, da se ne bo zgodilo, se je zgodilo. \n\u010ce malo pogledamo po medijih oziroma \u010dasopisih nekatere izjave predstavnikov vlade, lahko vidimo, da je avgusta predsednik Cerar rekel: \"Slovenija je pripravljena na prihod ve\u010djega \u0161tevila migrantov.\" Migranti so pa pre\u010dkali hrva\u0161ko-slovensko mejo preko nezavarovanih obmo\u010dij, \u0161li so \u010dez gozdove, sadovnjake, prebivalci Rigonc pa so bili na koncu z \u017eivci in potrpljenjem. Avgusta lanskega leta je dr\u017eavni sekretar \u0160efic rekel, da bodo migranti Slovenijo zgolj pre\u010dkali. Ja, zgodila pa se je razlika v \u0161tevilu migrantov. Septembra lanskega leta ste prav tako rekli: \"Poskrbljeno bo za varnost tako znotraj centrov kot v dr\u017eavi\". Dogajali pa so se pretepi znotraj nastanitvenih centrov, za\u017eiganje \u0161otorov, kraje na bencinskih \u010drpalkah in \u010de so to za vas, gospod dr\u017eavni sekretar, okoli\u0161\u010dine, ki so zna\u010dilne za varno dr\u017eavo, za nas to niso. V septembru je predsednik Vlade rekel: Slovenija se je odli\u010dno soo\u010dila z begunsko migrantsko krizo in postavila primer dobre prakse v EU. Zaskrbljeni ob\u010dani obmejnih krajev, smeti in \u010dlove\u0161ki iztrebki ter seveda opozorila EU in gro\u017enja z mini Schengenom, zaradi tega me mo\u010dno skrbi, \u010de je to dobra praksa za Slovenijo. Januarja leto\u0161njega leta je predsednik Vlade tudi rekel, da so za postavljanje tehni\u010dnih ovir krivi Hrvati. Prosim, to je va\u0161a ocena, o tem ocenjujete vi. Rekla bom, da me je kar po\u0161teno strah, ker je Vlada v mnenju za dana\u0161njo sejo zapisala bojazen, da bo Republika Slovenija prejela nazaj vse migrante, ki jih bodo v ciljnih dr\u017eavah zavrnili, je odve\u010d. Glede na vse navedbe prej, ki sem jih prebrala in ne dr\u017eijo, me mo\u010dno skrbi, da bomo vse te migrante pa\u010d dobili oziroma se bo to zgodilo. \nKo smo na mati\u010dnih delovnih telesih opozarjali na migrantsko krizo ste nam nekako vsi o\u010ditali, da se gremo populizem. Ko je na\u0161 predsednik, predsednik na\u0161e stranke, ob koncu avgusta podal sedem ukrepov za re\u0161itev iz teh krize, jih je Vlada lepo in \u010dedno prezrla, Evropa pa jih je seveda malo kasneje tudi vse povzela. \u010ce grem \u0161e naprej, konec oktobra se predsednik na\u0161e stranke ni udele\u017eil seje Sveta za nacionalno varnost. V pismu, ki ga je poslal Svetu, je opozoril na vse napake te vlade in podal osem predlogov oziroma ukrepov. Predlagal je: da Slovenija oblikuje operativno koordinacijsko skupino za obvladovanje migrantskih valov po vzoru koordinacijske skupine iz leta 1991; da Slovenija vzpostavi tehni\u010dne mo\u017enosti za nastavitev zapornih ograj na najbolj izpostavljenih delih meje; da Slovenija pospe\u0161eno dopolni oziroma ukrepi in pa usposobi prostovoljno rezervo Slovenske vojske in policije; da Slovenija takoj zagotovi izpla\u010dilo izrednih dodatkov policistom in vojakom ter ostalim zaposlenim, ki so izjemno obremenjeni z obvladovanjem migrantskih valov; da Slovenija preneha na\u010drtovati velike begunske centre za namestitev 5 tiso\u010d ali ve\u010d ljudi; da Slovenija zagotovi razbremenitev prebivalstva ob\u010dine Bre\u017eice in drugih obmejnih ob\u010din s prenosom administrativnih postopkov v ve\u010dje \u0161tevilo tranzitnih zbirnih centrov po celi dr\u017eavi; da se pospe\u0161eno zmanj\u0161uje razlika med \u0161tevilom migrantov, ki vstopajo v dr\u017eavo in pa tistimi, ki jo zapu\u0161\u010dajo; da se ob sprejemu migrantov iz humanitarnih in varnostnih razlogov takoj in dosledno lo\u010duje \u017eenske in otroke oziroma dru\u017eine kot najbolj ranljive skupine ter da se jih obravnava prednostno. Pismo je takrat predsednik na\u0161e stranke zaklju\u010dil s tem stavkom: \"Naj slovenska diplomacija kon\u010dno spet zaslu\u017ei denar, ki ga zanjo namenjajo davkopla\u010devalci.\" Na to njegovo pismo oziroma predloge se je odzval predsednik Vlade 28. oktobra na tiskovni konferenci, ko je to njegovo pisanje ocenil kot nedr\u017eavotvorno in poskus delitve Slovencev. Prebrala sem malo prej teh osem predlogov in vas zdaj spra\u0161ujem: Kateri od teh ukrepov je nedr\u017eavotvoren in kateri od teh ukrepov se vam zdi, da deli Slovence? To je tudi vpra\u0161anje za spo\u0161tovano ministrico.\nZa konec bom rekla tole, da je na\u0161e dr\u017eavljane strah. Strah jih je za njihovo varnost, blaginjo in nenazadnje \u2013priznajmo si \u2013 tudi za na\u0161o kulturo. Hvala lepa.",
        "speech_id": 520693
        }, {
        "content": "Predsednik, hvala lepa za besedo. Lep pozdrav vsem prisotnim. Za\u010dela bom s takimi besedami, kot sem za\u010dela pri razpravi na Dr\u017eavnem zboru ob sprejemanju prora\u010duna za leto 2016 in 2017 in sicer, da \u017ee samo Ministrstvo za zdravje potrebuje zdravnika, pa je \u010disto vseeno ali to koncesionar ali pa je iz javnega zdravstva. Zakaj tako mislim? \u017de kolegica Jelka Godec je prej omenila kaj se je dogajalo s pravilnikom o nujni medicinski pomo\u010di. Najprej kako je potekal postopek in tu se bom ustavila predvsem na objavi tega pravilnika in pa na priporo\u010dilo sklepa Dr\u017eavnega zbora in pa tega mati\u010dnega odbora.",
        "speech_id": 534332
        }
    }]
    """

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
    """
    * @api {get} getMembersOfPGs/ Get PGs and their members today
    * @apiName getMembersOfPGs
    * @apiGroup PGs
    * @apiDescription This function returns object with PG Parladata ids as keys.
      Each key corresponds to an array of integers containing Parladata ids of 
      all MPs that are members of the corresponging PG.

    * @apiSuccess {Object} / An object with PG ids as keys.
    * @apiSuccess {Integer[]} /.id An array of integers corresponding to members' Parladata ids.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersOfPGs/

    * @apiSuccessExample {json} Example response:
    {
        "1": [3, 14, 21, 39, 44, 68, 71, 74, 88, 16, 11, 27, 33, 40, 43, 57, 60, 70, 72, 19, 76, 77, 87, 89, 1354, 73, 84, 67, 48, 59, 92, 2933, 2934, 1357, 1355],
        "2": [4, 24],
        "3": [69, 22, 29, 34, 45, 52, 96, 85, 37, 41, 5],
        "4": [],
        "5": [10, 12, 26, 35, 51, 54, 55, 64, 66, 75, 36, 78, 25, 2, 23, 47, 53, 65, 91],
        "6": [32, 86, 63, 81, 17, 49],
        "7": [61, 62, 1356, 83, 30, 95],
        "8": [80, 82, 31, 42, 79, 58],
        "107": [],
        "108": [15],
        "109": [50, 9, 18, 7],
        "110": [],
        "111": [],
        "112": [],
        "97": [],
        "100": []
    }
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
    """
    * @api {get} getMembersOfPGsOnDate/{date} Get PGs and their members on a specific date
    * @apiName getMembersOfPGsOnDate
    * @apiGroup PGs
    * @apiDescription This function returns object with PG Parladata ids as keys.
      Each key corresponds to an array of integers containing Parladata ids of 
      all MPs that are members of the corresponging PG.

    * @apiParam {date} date The date for which memberships should be displayed.

    * @apiSuccess {Object} / An object with PG ids as keys.
    * @apiSuccess {Integer[]} /.id An array of integers corresponding to members' Parladata ids.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersOfPGsOnDate/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "1": [3, 14, 21, 39, 44, 68, 71, 74, 88, 16, 11, 27, 33, 40, 43, 57, 60, 70, 72, 19, 76, 77, 87, 89, 1354, 73, 84, 67, 48, 59, 92, 2933, 2934, 1357, 1355],
        "2": [4, 24],
        "3": [69, 22, 29, 34, 45, 52, 96, 85, 37, 41, 5],
        "4": [],
        "5": [10, 12, 26, 35, 51, 54, 55, 64, 66, 75, 36, 78, 25, 2, 23, 47, 53, 65, 91],
        "6": [32, 86, 63, 81, 17, 49],
        "7": [61, 62, 1356, 83, 30, 95],
        "8": [80, 82, 31, 42, 79, 58],
        "107": [],
        "108": [15],
        "109": [50, 9, 18, 7],
        "110": [],
        "111": [],
        "112": [],
        "97": [],
        "100": []
    }
    """

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
    * @api {get} getSpeechesOfMP/{id}/{?date} MP's speeches as strings
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
    """
    * @api {get} getMPParty/{id}/ MP's party
    * @apiName getMPParty
    * @apiGroup MPs
    * @apiDescription This function returns MP's party affiliation.
    * @apiParam {Integer} id MP's Parladata id.

    * @apiSuccess {String} acronym Party acronym.
    * @apiSuccess {String} name Full name of the party.
    * @apiSucess {Integer} id The MP's party's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMPParty

    * @apiSuccessExample {json} Example response:
    {
        "acronym": "SDS",
        "name": "PS Slovenska Demokratska Stranka",
        "id": 5
    }
    """

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
    """
    * @api {get} getNumberOfSeatsOfPG/{id}/ Number of PG's seats
    * @apiName getNumberOfSeatsOfPG
    * @apiGroup PGs
    * @apiDescription This function returns an object with the PG's id as the key
      and the number of seats for the desired PG.
    * @apiParam {Integer} id PG's id.

    * @apiSuccess {Integer} id The number of seats the PG with the same id as the key holds.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getNumberOfSeatsOfPG/1

    * @apiSuccessExample {json} Example response:
    {
        "1": 45
    }
    """

    value = dict()
    parliamentary_group = Organization.objects.filter(classification=PS,
                                                      id=int(pg_id))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    data = {pg.id: len([member.person.id for member in members.filter(organization=pg)]) for pg in parliamentary_group}
    value = {int(pg_id): data[int(pg_id)]}

    return JsonResponse(value, safe=False)


def getBasicInfOfPG(request, pg_id, date_=None):
    """Returns basic info of PG."""
    """
    * @api {get} getBasicInfoOfPG/{id}/{?date} PG's basic info
    * @apiName getBasicInfoOfPG
    * @apiGroup PGs
    * @apiDescription This function returns an object with the PG's basic info. If
      the date parameter is specified, it returns the info that was valid on that day.
    * @apiParam {Integer} id PG's id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Integer} AllVoters The number of voters that voted for this person.
    * @apiSuccess {Integer} HeadOfPG Parladata id of the person who heads the PG.
    * @apiSuccess {String} Twitter PG's Twitter url.
    * @apiSuccess {Integer} ViceOfPG Parladata id of the person who is the vice president of the PG.
    * @apiSuccess {String} Facebook PG's Facebook url.
    * @apiSuccess {String} Mail PG's official email.
    * @apiSuccess {Integer} NumberOfSeats Number of seats the PG holds in the parliament.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getBasicInfoOfPG/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getBasicInfoOfPG/2/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "AllVoters": 2957,
        "HeadOfPG": 24,
        "Twitter": null,
        "ViceOfPG": null,
        "Facebook": null,
        "Mail": "petra.jamnik@dz-rs.si",
        "NumberOfSeats": 2
    }
    """

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
    """
    * @api {get} getAllPGs/{?date} Get all PGs
    * @apiName getAllPGs
    * @apiGroup PGs
    * @apiDescription This function returns an object with all the PG's active on a given date.
      If no optional date parameter is given, it is assumed the date is today. It lists PGs in 
      an object with the PGs' Parladata ids as keys.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} id PG object with their id as key.
    * @apiSuccess {String} id.acronym The PG's acronym.
    * @apiSuccess {Boolean} id.is_coalition Is the PG in coalition with the government?
    * @apiSuccess {String} name The name of the PG.
    * @apiSuccess {Integer} id Parladata id of the PG.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllPGs/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllPGs/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "1": {
            "acronym": "SMC",
            "is_coalition": true,
            "name": "PS Stranka modernega centra",
            "id": 1
        },
        "2": {
            "acronym": "IMNS",
            "is_coalition": false,
            "name": "PS italijanske in mad\u017earske narodne skupnosti",
            "id": 2
        },
        "3": {
            "acronym": "DeSUS",
            "is_coalition": true,
            "name": "PS Demokratska Stranka Upokojencev Slovenije",
            "id": 3
        },
        "5": {
            "acronym": "SDS",
            "is_coalition": false,
            "name": "PS Slovenska Demokratska Stranka",
            "id": 5
        },
        "6": {
            "acronym": "NSI",
            "is_coalition": false,
            "name": "PS Nova Slovenija",
            "id": 6
        },
        "7": {
            "acronym": "SD",
            "is_coalition": true,
            "name": "PS Socialni Demokrati",
            "id": 7
        },
        "8": {
            "acronym": "ZL",
            "is_coalition": false,
            "name": "PS Zdru\u017eena Levica",
            "id": 8
        },
        "109": {
            "acronym": "PS NP",
            "is_coalition": false,
            "name": "PS nepovezanih poslancev ",
            "id": 109
        }
    }
    """

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
    """
    * @api {get} getAllPGsExt/{?date} Get all PGs with founded and disbanded dates
    * @apiName getAllPGsExt
    * @apiGroup PGs
    * @apiDescription This function returns an object with all the PG's active on a given date.
      If no optional date parameter is given, it is assumed the date is today. It lists PGs in 
      an object with the PGs' Parladata ids as keys.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} id PG object with their id as key.
    * @apiSuccess {String} id.acronym The PG's acronym.
    * @apiSuccess {date} id.founded Date when the PG was founded.
    * @apiSuccess {String} name The name of the PG.
    * @apiSuccess {date} id.disbanded Date when the PG was disbanded.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllPGsExt/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllPGsExt/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "1": {
            "acronym": "SMC",
            "founded": null,
            "name": "PS Stranka modernega centra",
            "disbanded": null
        },
        "2": {
            "acronym": "IMNS",
            "founded": null,
            "name": "PS italijanske in mad\u017earske narodne skupnosti",
            "disbanded": null
        },
        "3": {
            "acronym": "DeSUS",
            "founded": null,
            "name": "PS Demokratska Stranka Upokojencev Slovenije",
            "disbanded": null
        },
        "4": {
            "acronym": "ZAAB",
            "founded": "2014-08-01T00:00:00",
            "name": "PS Zavezni\u0161tvo Alenke Bratu\u0161ek",
            "disbanded": "2015-09-08T00:00:00"
        },
        "5": {
            "acronym": "SDS",
            "founded": "2014-08-01T00:00:00",
            "name": "PS Slovenska Demokratska Stranka",
            "disbanded": null
        },
        "6": {
            "acronym": "NSI",
            "founded": null,
            "name": "PS Nova Slovenija",
            "disbanded": null
        },
        "7": {
            "acronym": "SD",
            "founded": null,
            "name": "PS Socialni Demokrati",
            "disbanded": null
        },
        "8": {
            "acronym": "ZL",
            "founded": "2014-08-06T00:00:00",
            "name": "PS Zdru\u017eena Levica",
            "disbanded": null
        },
        "109": {
            "acronym": "PS NP",
            "founded": "2016-01-29T00:00:00",
            "name": "PS nepovezanih poslancev ",
            "disbanded": null
        },
        "97": {
            "acronym": "PS NP",
            "founded": "2015-09-14T00:00:00",
            "name": "PS nepovezanih poslancev ",
            "disbanded": "2016-01-28T00:00:00"
        }
    }
    """

    parliamentary_group = Organization.objects.filter(classification=PS)
    data = {pg.id: {'name': pg.name,
                    'acronym': pg.acronym,
                    'founded': pg.founding_date,
                    'disbanded': pg.dissolution_date} for pg in parliamentary_group}

    return JsonResponse(data, safe=False)


def getAllOrganizations(request):
    """Returns all organizations."""
    """
    * @api {get} getAllOrganizations/{?date} Get all Organizations
    * @apiName getAllOrganizations
    * @apiGroup Other
    * @apiDescription This function returns an object with all the organizations active on a given date.
      If no optional date parameter is given, it is assumed the date is today. It lists organizations in 
      an object with the organizations' Parladata ids as keys.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} id PG object with their id as key.
    * @apiSuccess {String} id.acronym The organization's acronym.
    * @apiSuccess {String} name The name of the organization.
    * @apiSuccess {Boolean} id.is_coalition Is the organization in coalition with the government?

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllOrganizations/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllOrganizations/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "8": {
            "acronym": "ZL",
            "name": "PS Zdru\u017eena Levica",
            "classification": "poslanska skupina",
            "is_coalition": false
        },
        "9": {
            "acronym": "",
            "name": "Kolegij predsednika dr\u017eavnega zbora",
            "classification": "kolegij",
            "is_coalition": false
        },
        "10": {
            "acronym": "",
            "name": "Komisija za nadzor javnih financ",
            "classification": "komisija",
            "is_coalition": false
        },
        "11": {
            "acronym": "",
            "name": "Komisija za narodni skupnosti",
            "classification": "komisija",
            "is_coalition": false
        }
    }
    """

    org = Organization.objects.all()
    data = {pg.id: {'name': pg.name,
                    'classification': pg.classification,
                    'acronym': pg.acronym,
                    'is_coalition': True if pg.is_coalition == 1 else False} for pg in org}

    return JsonResponse(data)


# TODO Filip napiši pravi opis metode :) Ta metoda vrne vse govore (tudi gostov) in se uporablja za export govorov v parlalize.
def getAllSpeeches(request, date_=None):
    """Returns all speeches."""
    """
    * @api {get} getAllSpeeches/{?date} Get all Speeches
    * @apiName getAllSpeeches
    * @apiGroup Other
    * @apiDescription This function returns an object with all the organizations active on a given date.
      If no optional date parameter is given, it is assumed the date is today. It lists organizations in 
      an object with the organizations' Parladata ids as keys.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} id PG object with their id as key.
    * @apiSuccess {String} id.acronym The organization's acronym.
    * @apiSuccess {String} name The name of the organization.
    * @apiSuccess {Boolean} id.is_coalition Is the organization in coalition with the government?

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllOrganizations/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllOrganizations/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "8": {
            "acronym": "ZL",
            "name": "PS Zdru\u017eena Levica",
            "classification": "poslanska skupina",
            "is_coalition": false
        },
        "9": {
            "acronym": "",
            "name": "Kolegij predsednika dr\u017eavnega zbora",
            "classification": "kolegij",
            "is_coalition": false
        },
        "10": {
            "acronym": "",
            "name": "Komisija za nadzor javnih financ",
            "classification": "komisija",
            "is_coalition": false
        },
        "11": {
            "acronym": "",
            "name": "Komisija za narodni skupnosti",
            "classification": "komisija",
            "is_coalition": false
        }
    }
    """

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


def getVotes(request, date_=None):
    """Returns all votes."""
    """
    * @api {get} getVotes/{date} Get all Votes up until a date
    * @apiName getVotes
    * @apiGroup Votes
    * @apiDescription This function returns a list of all votes that
      took place until a given date.

    * @apiSuccess {Object[]} / List of vote objects
    * @apiSuccess {date} /.start_time Vote's start time in UTF-8 datetime as string.
    * @apiSuccess {String} /.motion Motion name - what is the vote about.
    * @apiSuccess {Integer} /.session Session's at which the vote took place parladata id.
    * @apiSuccess {date} /.start_time Vote's end time in UTF-8 datetime as string. Currently return null.
    * @apiSuccess {Integer} /.organization_id Parladata id of the organization in which the vote took place.
    * @apiSuccess {Integer} /.id Parladata id of the vote.
    * @apiSuccess {String} /.result String with the result of the vote. Currently always returns "-".

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getVotes/12.12.2016

    * @apiSuccessExample {json} Example response:
    [
        {
            "start_time": "2014-08-01T12:16:54",
            "motion": "Dnevni red v celoti",
            "session": 6684,
            "end_time": null,
            "party": 95,
            "id": 6513,
            "result": "-"
        }, {
            "start_time": "2014-08-01T12:43:48",
            "motion": "Proceduralni predlog za prekinitev 1. to\u010dke dnevnega reda",
            "session": 6684,
            "end_time": null,
            "party": 95,
            "id": 6512,
            "result": "-"
        }, {
            "start_time": "2014-08-01T12:49:10",
            "motion": "Sklep o imenovanju predsednika in podpredsednika Mandatno-volilne komisije - Sklep",
            "session": 6684,
            "end_time": null,
            "party": 95,
            "id": 6511,
            "result": "-"
        }, {
            "start_time": "2014-08-01T14:18:26",
            "motion": "Poro\u010dilo o izidu pred\u010dasnih volitev v Dr\u017eavni zbor Republike Slovenije - Glasovanje o predlogu sklepa",
            "session": 6684,
            "end_time": null,
            "party": 95,
            "id": 6510,
            "result": "-"
        }
    ]
    """
    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date() + timedelta(days=1) - timedelta(minutes=1)
    else:
        fdate = datetime.now().date() + timedelta(days=1) - timedelta(minutes=1)
    data = []

    votes = Vote.objects.filter(start_time__lte=fdate).order_by("start_time")
    for vote in votes:
        data.append({'id': vote.id,
                     'motion': vote.motion.text,
                     'organization_id': vote.organization.id,
                     'session': vote.session.id,
                     'start_time': vote.start_time,
                     'end_time': vote.end_time,
                     'result': vote.result})

    return JsonResponse(data, safe=False)


def getAllBallots(request, date_=None):
    """Returns all ballots."""
    """
    * @api {get} getAllBallots/{?date} Get all Ballots
    * @apiName getAllBallots
    * @apiGroup Votes
    * @apiDescription This function returns a list of all ballots
      submitted until a given date. If no date is supplied it is assumed
      the date is today.

    * @apiSuccess {Object[]} / List of vote objects
    * @apiSuccess {Integer} /.vote Parladata ID of the vote.
    * @apiSuccess {Integer} /.voter Parladata ID of the MP who submitted the ballot.
    * @apiSuccess {Integer} /.id Parladata ID of the ballot.
    * @apiSuccess {String} /.option The option of the ballot (za, proti, kvorum, ni).

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllBallots
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllBallots/12.12.2016

    * @apiSuccessExample {json} Example response:
    [
        {
            "vote": 6601,
            "voter": 95,
            "id": 593806,
            "option": "za"
        }, {
            "vote": 6601,
            "voter": 2,
            "id": 593807,
            "option": "kvorum"
        }, {
            "vote": 6601,
            "voter": 3,
            "id": 593808,
            "option": "za"
        }, {
            "vote": 6601,
            "voter": 4,
            "id": 593809,
            "option": "ni"
        }
    ]
    """

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
    else:
        fdate = datetime.now().date()

    data = [model_to_dict(ballot,
                          fields=['id', 'vote', 'voter', 'option'], exclude=[])
            for ballot in Ballot.objects.filter(vote__start_time__lte=fdate)]

    return JsonResponse(data, safe=False)


def getAllPeople(request):
    """Returns all people."""
    """
    * @api {get} getAllPeople Get all People
    * @apiName getAllPeople
    * @apiGroup Other
    * @apiDescription This function returns a list of all people in Parladata.
      This includes people who only spoke in the parliament as well as MPs and
      government members. The objects returned resemble those of getMPStatic,
      but keep in mind, that for people who only spoke in the parliament, no
      extra information is collected.

    * @apiSuccess {Object[]} / List of person objects.
    * @apiSuccess {String} /.gov_id MP's "government id". The ID this
      particular MP is given on http://www.dz-rs.si
      If not returns null.
    * @apiSuccess {Integer} /.voters The number of voters the MP was elected with.
      Only MPs have voters.
    * @apiSuccess {String} /.image URL to the person's image on http://www.dz-rs.si.
    * @apiSuccess {String} /.patronymic_name The person's patronymic name if applicable.
      If not returns empty string.
    * @apiSuccess {String} /.sort_name The person's sorting name if applicable.
      If not returns empty string.
    * @apiSuccess {Integer} /.id The person's Parladata id.
    * @apiSuccess {String} /.biography The person's biography if applicable.
    * @apiSuccess {String} /.classification The person's classification if applicable.
      If not returns empty string. Sometimes used for internal sorting purposes.
    * @apiSuccess {String} /.district Name of the district (or districts) the MP was elected in.
      Only MP's have districts. Currently always returns empty string. TODO
    * @apiSuccess {String} /.additional_name The person's additional name if applicable.
      If not returns empty string.
    * @apiSuccess {String} /.hovorific_suffix The person's honorific suffix, such as "PhD".
    * @apiSuccess {String} /.honorific_prefix The person's honorific prefix name if applicable.
      If not returns empty string.
    * @apiSuccess {String} /.given_name The person's given name.
    * @apiSuccess {String} /.email The person's email.
    * @apiSuccess {String} /.membership The person's current party.
    * @apiSuccess {Boolean} /.active The person's active state.
    * @apiSuccess {String} /.family_name The person's family name.
    * @apiSuccess {String} /.name The person's full/display name.
    * @apiSuccess {String} /.gov_picture_url URL to Person's image on http://www.dz-rs.si if applicable.
    * @apiSuccess {String} /.summary Person's summary if applicable. If not returns empty string.
    * @apiSuccess {String} /.birth_date Person's date of birth. Returns time as well, so that all
      objects are datetime, but the time can be ignored.
    

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllPeople/

    * @apiSuccessExample {json} Example response:
    [
        {
            "gov_id": null,
            "voters": null,
            "image": null,
            "patronymic_name": null,
            "sort_name": null,
            "id": 1329,
            "biography": null,
            "classification": null,
            "district": "",
            "additional_name": null,
            "honorific_suffix": null,
            "honorific_prefix": null,
            "given_name": null,
            "email": null,
            "membership": "",
            "active": true,
            "family_name": null,
            "name": "Mateja Ko\u017euh Novak",
            "gov_picture_url": null,
            "gender": null,
            "death_date": "None",
            "summary": null,
            "birth_date": "None"
        }, {
            "gov_id": null,
            "voters": null,
            "image": null,
            "patronymic_name": null,
            "sort_name": null,
            "id": 1331,
            "biography": null,
            "classification": null,
            "district": "",
            "additional_name": null,
            "honorific_suffix": null,
            "honorific_prefix": null,
            "given_name": null,
            "email": null,
            "membership": null,
            "active": true,
            "family_name": null,
            "name": "Vlasta Nussdorfer",
            "gov_picture_url": null,
            "gender": null,
            "death_date": "None",
            "summary": null,
            "birth_date": "None"
        }, {
            "gov_id": "P225",
            "voters": 2496,
            "image": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P225",
            "patronymic_name": "",
            "sort_name": "",
            "id": 15,
            "biography": "",
            "classification": "",
            "district": "",
            "additional_name": "",
            "honorific_suffix": "mag.",
            "honorific_prefix": "",
            "given_name": "Andrej",
            "email": "andrej.cus@dz-rs.si",
            "membership": "Nepovezani poslanec Andrej \u010cu\u0161",
            "active": true,
            "family_name": "\u010cu\u0161",
            "name": "Andrej \u010cu\u0161",
            "gov_picture_url": "http://www.dz-rs.si/wps/PA_DZ-LN-Osebe/CommonRes?idOseba=P225",
            "gender": "male",
            "death_date": "None",
            "summary": "",
            "birth_date": "1990-07-29 02:00:00"
        }
    ]
    """
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
                     'email': '',
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
    """
    * @api {get} motionOfSession/{id} Get all votes on a specific Session
    * @apiName motionOfSession
    * @apiGroup Sessions
    * @apiDescription This function returns a list of all motions voted upon
      in a specific session.

    * @apiSuccess {Object[]} / List of Motion objects.
    * @apiSuccess {Object[]} /.doc_url List of document objects that belong to the motion.
    * @apiSuccess {String} /.doc_url.url Document URL.
    * @apiSuccess {String} /.doc_url.name Document name.
    * @apiSuccess {String[]} /.tags An array of tags that belong to the motion.
    * @apiSuccess {String} /.text Motion text (what the motion is about).
    * @apiSuccess {date} /.start_time Motion start time as string.
    * @apiSuccess {Boolean} /.result Returns true if the motion passed, false if it didn't null if we don't know.
    * @apiSuccess {Integer} /.vote_id Parladata id of the vote that took place for this motion.
    * @apiSuccess {Integer} /.id Parladata id of the motion.
      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/motionOfSession/9158

    * @apiSuccessExample {json} Example response:
    [
        {
            "doc_url": [{
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005b2b645b53a0715714f6ae78cb5276f4b6144a93f432b13c76b532975",
            "name": "Dopis Dr\u017eavnemu svetu | Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov"
            }, {
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005af6c4e0407faa583537d72f288c917218a4f7202b119a68253c7b302",
            "name": "Besedilo zakona poslano Dr\u017eavnemu svetu | Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov"
            }, {
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e00555897ad23d4b3750966a27416b777766702e97964fb34b8ecec49f96",
            "name": " | Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov"
            }],
            "tags": ["Odbor za finance in monetarno politiko"],
            "text": "Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov - Amandma: K 25. \u010dlenu 7.2.2017 [SMC - Poslanska skupina Stranke modernega centra]",
            "start_time": "2017-02-15T16:18:28",
            "result": true,
            "vote_id": 6894,
            "id": 6650
        }, {
            "doc_url": [{
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005b2b645b53a0715714f6ae78cb5276f4b6144a93f432b13c76b532975",
            "name": "Dopis Dr\u017eavnemu svetu | Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov"
            }, {
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005af6c4e0407faa583537d72f288c917218a4f7202b119a68253c7b302",
            "name": "Besedilo zakona poslano Dr\u017eavnemu svetu | Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov"
            }],
            "tags": ["Odbor za finance in monetarno politiko"],
            "text": "Zakon o spremembah in dopolnitvah Zakona o trgu finan\u010dnih instrumentov - Amandma: K 51. \u010dlenu 7.2.2017 [SMC - Poslanska skupina Stranke modernega centra]",
            "start_time": "2017-02-15T16:19:22",
            "result": true,
            "vote_id": 6893,
            "id": 6649
        }
    ]
    """

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


def getBallotsOfSession(request, id_se):
    """Returns all ballots of specific Session. TODO"""
    """
    * @api {get} getBallotsOfSession/{id} Get all ballots from a specific Session
    * @apiName getBallotsOfSession
    * @apiGroup Sessions
    * @apiDescription This function returns a list of all ballots for all motions voted
      upon in this session.

    * @apiSuccess {Object[]} / List of Ballot objects.
    * @apiSuccess {String} /.Acronym PG acronym for MP's PG.
    * @apiSuccess {Integer} /.pg_id Parladata id of the PG the MP that submitted the ballot belongs to.
    * @apiSuccess {Integer} /.mo_id Parladata id of the motion this ballot belongs to.
    * @apiSuccess {String} /.option The option on the ballot. One of "za", "proti", "kvorum", "ni").
      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getBallotsOfSession/9158

    * @apiSuccessExample {json} Example response:
    [
        {
            "Acronym": "SDS",
            "pg_id": 5,
            "mp_id": 91,
            "mo_id": 6650,
            "option": "kvorum"
        }, {
            "Acronym": "SMC",
            "pg_id": 1,
            "mp_id": 89,
            "mo_id": 6650,
            "option": "za"
        }, {
            "Acronym": "SMC",
            "pg_id": 1,
            "mp_id": 88,
            "mo_id": 6650,
            "option": "za"
        }, {
            "Acronym": "SMC",
            "pg_id": 1,
            "mp_id": 87,
            "mo_id": 6650,
            "option": "za"
        }, {
            "Acronym": "NSI",
            "pg_id": 6,
            "mp_id": 86,
            "mo_id": 6650,
            "option": "kvorum"
        }, {
            "Acronym": "DeSUS",
            "pg_id": 3,
            "mp_id": 85,
            "mo_id": 6650,
            "option": "za"
        }
    ]
    """

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


def getBallotsOfMotion(request, motion_id):
    """Returns all ballots of specific motion. TODO"""
    """
    * @api {get} getBallotsOfMotion/{id} Get all ballots from a specific motion
    * @apiName getBallotsOfMotion
    * @apiGroup Votes
    * @apiDescription This function returns a list of all ballots for a specific motion.

    * @apiSuccess {Object[]} / List of Ballot objects.
    * @apiSuccess {String} /.Acronym PG acronym for MP's PG.
    * @apiSuccess {Integer} /.pg_id Parladata id of the PG the MP that submitted the ballot belongs to.
    * @apiSuccess {Integer} /.mo_id Parladata id of the motion this ballot belongs to.
    * @apiSuccess {String} /.option The option on the ballot. One of "za", "proti", "kvorum", "ni").
      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getBallotsOfMotion/6650

    * @apiSuccessExample {json} Example response:
    [
        {
            "Acronym": "SD",
            "pg_id": 7,
            "mp_id": 95,
            "mo_id": 6406,
            "option": "za"
        }, {
            "Acronym": "SDS",
            "pg_id": 5,
            "mp_id": 2,
            "mo_id": 6406,
            "option": "za"
        }, {
            "Acronym": "SMC",
            "pg_id": 1,
            "mp_id": 3,
            "mo_id": 6406,
            "option": "za"
        }, {
            "Acronym": "IMNS",
            "pg_id": 2,
            "mp_id": 4,
            "mo_id": 6406,
            "option": "ni"
        }, {
            "Acronym": "DeSUS",
            "pg_id": 3,
            "mp_id": 5,
            "mo_id": 6406,
            "option": "za"
        }
    ]
    """

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
    """
    * @api {get} getNumberOfPersonsSessions/{id}/{?date} Get MP's number of attended sessions
    * @apiName getNumberOfPersonsSessions
    * @apiGroup MPs
    * @apiDescription This function returns an object with the calculated presence for a specific person up until
      a given date. If no date is supplied it is assumed the date is today.

    * @apiSuccess {Object} / 
    * @apiSuccess {Integer} /.sessions_with_speeches The number of sessions this person spoke at at least once.
    * @apiSuccess {Integer} /.all_sessions The number of sessions this person either voted or spoke at.
    * @apiSuccess {Integer} /.session_with_vote The number of sessions this person voted on at least once.
      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getNumberOfPersonsSessions/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getNumberOfPersonsSessions/2/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "sessions_with_speech": 107,
        "all_sessions": 119,
        "sessions_with_vote": 39
    }
    """

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


def getMembersOfPGsRanges(request, date_=None):
    """
    Returns all memberships(start date, end date and members
    in this dates) of all PGs from start of mandate to end date
    which is an argument of method.
    """
    """
    * @api {get} getMembersOfPGsRanges/{?date} Get membership ranges for all PGs
    * @apiName getMembersOfPGsRanges
    * @apiGroup PGs
    * @apiDescription This function returns a list of objects representing uninterupted
      membership constellations in the national assembly. In other words, it returns as many
      objects as there were different membership settings. If no date is specified it is assumed
      the date is today, otherwise the results returned span only until the supplied date.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {Object} /.members Object with PG Parladata ids as keys.
    * @apiSuccess {Integer[]} /.members.PG_ID List of Parladata ids for all members of this PG in the current timespan.
    * @apiSuccess {date} /.start_date This range's start date (from).
    * @apiSuccess {date} /.end_date This range's end date (to).      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersOfPGsRanges/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMembersOfPGsRanges/12.12.2015

    * @apiSuccessExample {json} Example response:
    [
        {
            "members": {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],
            "6": [],
            "7": [],
            "8": [],
            "107": [],
            "108": [],
            "109": [],
            "110": [],
            "111": [],
            "112": [],
            "97": [],
            "100": [],
            "124": [],
            "125": []
            },
            "start_date": "31.07.2014",
            "end_date": "31.07.2014"
        }, {
            "members": {
            "1": [3, 14, 21, 39, 44, 68, 71, 74, 88, 16, 11, 27, 33, 40, 43, 57, 60, 70, 72, 19, 76, 77, 87, 89, 18, 56, 73, 84, 67, 28, 48, 6, 8, 50, 46, 13],
            "2": [4, 24],
            "3": [69, 22, 29, 34, 45, 52, 20, 37, 41, 5],
            "4": [59, 9, 85, 7],
            "5": [10, 12, 26, 35, 51, 54, 55, 64, 66, 75, 15, 49, 36, 78, 25, 2, 23, 47, 53, 65, 91],
            "6": [32, 86, 63, 81, 17],
            "7": [61, 62, 38, 83, 90, 30],
            "8": [80, 82, 31, 79, 58, 42],
            "107": [],
            "108": [],
            "109": [],
            "110": [],
            "111": [],
            "112": [],
            "97": [],
            "100": [],
            "124": [],
            "125": []
            },
            "start_date": "01.08.2014",
            "end_date": "25.08.2014"
        }, {
            "members": {
            "1": [3, 14, 21, 39, 44, 68, 71, 74, 88, 16, 11, 27, 33, 40, 43, 57, 60, 70, 72, 19, 76, 77, 87, 89, 18, 56, 73, 84, 67, 28, 48, 6, 8, 50, 46],
            "2": [4, 24],
            "3": [69, 22, 29, 34, 45, 52, 20, 37, 41, 5],
            "4": [59, 9, 85, 7],
            "5": [10, 12, 26, 35, 51, 54, 55, 64, 66, 75, 15, 49, 36, 78, 25, 2, 23, 47, 53, 65, 91],
            "6": [32, 86, 63, 81, 17],
            "7": [61, 62, 38, 83, 90, 30],
            "8": [80, 82, 31, 79, 58, 42],
            "107": [],
            "108": [],
            "109": [],
            "110": [],
            "111": [],
            "112": [],
            "97": [],
            "100": [],
            "124": [],
            "125": []
            },
            "start_date": "26.08.2014",
            "end_date": "26.08.2014"
        }
    ]
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
    """
    * @api {get} getMembersOfPGRanges/{id}/{?date} Get membership ranges for a specific PGs
    * @apiName getMembersOfPGRanges
    * @apiGroup PGs
    * @apiDescription This function returns a list of objects representing uninterupted
      membership constellations in a single PG. In other words, it returns as many
      objects as there were different membership settings. If no date is specified it is assumed
      the date is today, otherwise the results returned span only until the supplied date.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {Integer[]} /.members List of Parladata ids for all members of this PG in the current timespan.
    * @apiSuccess {date} /.start_date This range's start date (from).
    * @apiSuccess {date} /.end_date This range's end date (to).      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersOfPGRanges/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMembersOfPGRanges/2/12.12.2015

    * @apiSuccessExample {json} Example response:
    [
        {
            "members": [],
            "start_date": "31.07.2014",
            "end_date": "31.07.2014"
        }, {
            "members": [4, 24],
            "start_date": "01.08.2014",
            "end_date": "17.03.2017"
        }
    ]
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
    """Returns all memberships of specific MP. TODO"""
    """
    * @api {get} getMembershipsOfMember/{id}/{?date} Get memberships of an MP
    * @apiName getMembershipsOfMember
    * @apiGroup MPs
    * @apiDescription This function returns an object with keys representing groups
      of organisations this person belongs to. If no date is specified it is assumed the
      date is today, otherwise the results returned correspond to the state of the MPs
      memberships on that specific date.

    * @apiSuccess {Object[]} /
    * @apiSuccess {Object[]} /.delegacija List of membership objects in "delegations".
    * @apiSuccess {String} /.delegacija.url The organizations public URL if applicable.
    * @apiSuccess {String} /.delegacija.org_type The organization type.
    * @apiSuccess {Integer} /.delegacija.org_id The organization's Parladata id.
    * @apiSuccess {String} /.delegacija.name The organization's name.
    * @apiSuccess {Object[]} /.odbor List of membership objects in "delegations".
    * @apiSuccess {String} /.odbor.url The organizations public URL if applicable.
    * @apiSuccess {String} /.odbor.org_type The organization type.
    * @apiSuccess {Integer} /.odbor.org_id The organization's Parladata id.
    * @apiSuccess {String} /.odbor.name The organization's name.
    * @apiSuccess {Object[]} /.poslanska_skupina List of membership objects in "delegations".
    * @apiSuccess {String} /.poslanska_skupina.url The organizations public URL if applicable.
    * @apiSuccess {String} /.poslanska_skupina.org_type The organization type.
    * @apiSuccess {Integer} /.poslanska_skupina.org_id The organization's Parladata id.
    * @apiSuccess {String} /.poslanska_skupina.name The organization's name.
    * @apiSuccess {Object[]} /.komisija List of membership objects in "delegations".
    * @apiSuccess {String} /.komisija.url The organizations public URL if applicable.
    * @apiSuccess {String} /.komisija.org_type The organization type.
    * @apiSuccess {Integer} /.komisija.org_id The organization's Parladata id.
    * @apiSuccess {String} /.komisija.name The organization's name.
    * @apiSuccess {Object[]} /.skupina_prijateljstva List of membership objects in "delegations".
    * @apiSuccess {String} /.skupina_prijateljstva.url The organizations public URL if applicable.
    * @apiSuccess {String} /.skupina_prijateljstva.org_type The organization type.
    * @apiSuccess {Integer} /.skupina_prijateljstva.org_id The organization's Parladata id.
    * @apiSuccess {String} /.skupina_prijateljstva.name The organization's name.


    * @apiSuccess {Integer[]} /.members List of Parladata ids for all members of this PG in the current timespan.
    * @apiSuccess {date} /.start_date This range's start date (from).
    * @apiSuccess {date} /.end_date This range's end date (to).      

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembershipsOfMember/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMembershipsOfMember/2/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "delegacija": [{
            "url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/StalnaDelegacija?idSD=SD003",
            "org_type": "delegacija",
            "org_id": 32,
            "name": "Delegacija Dr\u017eavnega zbora v Parlamentarni skup\u0161\u010dini Organizacije za varnost in sodelovanje v Evropi"
        }],
        "odbor": [{
            "url": null,
            "org_type": "odbor",
            "org_id": 25,
            "name": "Odbor za pravosodje"
        }, {
            "url": null,
            "org_type": "odbor",
            "org_id": 23,
            "name": "Odbor za notranje zadeve, javno upravo in lokalno samoupravo"
        }, {
            "url": null,
            "org_type": "odbor",
            "org_id": 22,
            "name": "Odbor za kulturo"
        }, {
            "url": null,
            "org_type": "odbor",
            "org_id": 24,
            "name": "Odbor za obrambo"
        }],
        "poslanska skupina": [{
            "url": "https://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/PoslanskaSkupina?idPS=PS012",
            "org_type": "poslanska skupina",
            "org_id": 5,
            "name": "PS Slovenska Demokratska Stranka"
        }],
        "komisija": [{
            "url": null,
            "org_type": "komisija",
            "org_id": 15,
            "name": "Mandatno-volilna komisija"
        }],
        "skupina prijateljstva": [{
            "url": "http://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/KdoJeKdo/SkupinaPrijateljstva?idSP=SP044",
            "org_type": "skupina prijateljstva",
            "org_id": 79,
            "name": "Skupina prijateljstva z Veliko Britanijo"
        }]
    }
    """

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
                     in set([member.organization.classification.replace(' ', '_')
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
        classification = out_init_dict[mem.organization.classification.replace(' ', '_')]
        classification.append({'org_type': mem.organization.classification,
                               'org_id': mem.organization.id,
                               'name': mem.organization.name,
                               'url': url})
    return JsonResponse(out_init_dict)


def getAllTimeMemberships(request):
    """Returns all memberships of all MPs."""
    """
    * @api {get} getAllTimeMemberships Get all membership times of all MPs
    * @apiName getAllTimeMemberships
    * @apiGroup MPs
    * @apiDescription This function returns a list of objects representing membership streaks
      for individual MPs. Iterating through these objects will give you a complete picture of when
      an MP was a member of the national assembly.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {date} /.start_time Membership start time (from).
    * @apiSuccess {date} /.end_time Membership end time (to).
    * @apiSuccess {Integer} /.id The person's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllTimeMemberships

    * @apiSuccessExample {json} Example response:
    [
        {
            "start_time": "2014-08-01T00:00:00",
            "end_time": null,
            "id": 69
        }, {
            "start_time": "2014-08-01T00:00:00",
            "end_time": null,
            "id": 80
        }, {
            "start_time": "2014-08-01T00:00:00",
            "end_time": null,
            "id": 82
        }, {
            "start_time": "2014-08-01T00:00:00",
            "end_time": null,
            "id": 3
        }, {
            "start_time": "2014-08-01T00:00:00",
            "end_time": null,
            "id": 14
        }
    ]
    """

    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(organization__in=parliamentary_group)
    return JsonResponse([{"start_time": member.start_time,
                          "end_time": member.end_time,
                          "id": member.person.id} for member in members],
                        safe=False)


def getOrganizatonsByClassification(request):
    """Returns organizations by classification(working bodies, PG, council). TODO"""
    """
    * @api {get} getOrganizatonsByClassification Get all Organizations organized by classification
    * @apiName getOrganizatonsByClassification
    * @apiGroup Other
    * @apiDescription This function returns an object with the keys corresponding to different
      organization classifications.

    * @apiSuccess {Object[]} /
    * @apiSuccess {Object[]} /.working_bodies Organizations classified as working bodies.
    * @apiSuccess {Integer} /.working_bodies.id The organization's Parladata id.
    * @apiSuccess {String} /.working_bodies.name The organization's name.
    * @apiSuccess {Object[]} /.parliamentary_groups Organizations classified as PGs.
    * @apiSuccess {Integer} /.parliamentary_groups.id The organization's Parladata id.
    * @apiSuccess {String} /.parliamentary_groups.name The organization's name.
    * @apiSuccess {Object[]} /.council Organizations classified as councils.
    * @apiSuccess {Integer} /.council.id The organization's Parladata id.
    * @apiSuccess {String} /.council.name The organization's name.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getOrganizatonsByClassification

    * @apiSuccessExample {json} Example response:
    {
        "working_bodies": [{
            "id": 22,
            "name": "Odbor za kulturo"
        }, {
            "id": 26,
            "name": "Odbor za zadeve Evropske unije"
        }, {
            "id": 27,
            "name": "Odbor za zdravstvo"
        }, {
            "id": 24,
            "name": "Odbor za obrambo"
        }, {
            "id": 29,
            "name": "Ustavna komisija"
        }],
        "parliamentary_groups": [{
            "id": 4,
            "name": "PS Zavezni\u0161tvo Alenke Bratu\u0161ek"
        }, {
            "id": 7,
            "name": "PS Socialni Demokrati"
        }, {
            "id": 1,
            "name": "PS Stranka modernega centra"
        }, {
            "id": 6,
            "name": "PS Nova Slovenija"
        }, {
            "id": 125,
            "name": "Stranka modernega centra"
        }],
        "council": [{
            "id": 9,
            "name": "Kolegij predsednika dr\u017eavnega zbora"
        }]
    }
    """

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
    """
    * @api {get} getTags Get all Tags
    * @apiName getTags
    * @apiGroup Other
    * @apiDescription This function returns a list of objects representing individual
      tags used for tagging motions.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {String} /.name The tag's name.
    * @apiSuccess {Integer} /.id The tag's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getTags

    * @apiSuccessExample {json} Example response:
    [
        {
            "name": "Komisija za nadzor javnih financ",
            "id": 13
        }, {
            "name": "Kolegij predsednika Dr\u017eavnega zbora",
            "id": 12
        }, {
            "name": "Komisija za narodni skupnosti",
            "id": 14
        }, {
            "name": "Komisija za odnose s Slovenci v zamejstvu in po svetu",
            "id": 15
        }
    ]
    """

    out = [{"name": tag.name,
            "id": tag.id} for tag in Tag.objects.all().exclude(id__in=[1, 2, 3, 4, 5, 8, 9])]

    return JsonResponse(out, safe=False)


def getDistricts(request):
    """Returns all districts."""
    """
    * @api {get} getDistricts Get all Districts
    * @apiName getDistricts
    * @apiGroup Other
    * @apiDescription This function returns a list of objects representing individual
      voting districts.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {String} /.name The district's name.
    * @apiSuccess {Integer} /.id The district's Parladata id.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getDistricts

    * @apiSuccessExample {json} Example response:
    [
        {
            "id": 89,
            "name": "Ajdov\u0161\u010dina"
        }, {
            "id": 88,
            "name": "Nova Gorica I"
        }, {
            "id": 87,
            "name": "Nova Gorica II"
        }, {
            "id": 86,
            "name": "Postojna"
        }
    ]
    """

    out = [{"id": area.id,
            "name": area.name} for area in Area.objects.filter(calssification="okraj")]

    return JsonResponse(out, safe=False)


def getSpeechData(request, speech_id):
    """Returns data of specific speech."""
    """
    * @api {get} getSpeechData Get info about a speech
    * @apiName getSpeechData
    * @apiGroup Other
    * @apiDescription This function returns an object with the speech's basic info.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {String} /.date The date of the speech.
    * @apiSuccess {String} /.session_name The name of the session at which the speech took place.
    * @apiSuccess {Integer} /.session_id The Parladata id of the session at which the speech took place.
    * @apiSuccess {Integer} /.speaker_id Parladata id of the speaker who said the words.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getSpeechData/996415

    * @apiSuccessExample {json} Example response:
    {
        "date": "2017-01-18",
        "session_name": "69. redna seja",
        "id": 996415,
        "session_id": 8935,
        "speaker_id": 39
    }
    """

    speech = Speech.objects.filter(pk=speech_id)

    if len(speech) > 0:
        speech = speech[0]

        output = {
            'id': int(speech_id),
            'date': speech.session.start_time.date(),
            'speaker_id': speech.speaker.id,
            'session_id': speech.session.id,
            'session_name': speech.session.name,
            'start_time': speech.start_time,
            'order': speech.order
        }

        return JsonResponse(output, safe=False)

    return HttpResponse(-1)


def getResultOfMotion(request, motion_id): # TODO refactor delete
    """Returns result of motion/vote."""

    output = {"result": Motion.objects.get(id=motion_id).result}

    return JsonResponse(output, safe=False)


def getPersonData(request, person_id):
    """Returns data of specific person.
       Method is used for data enrichment in parlalize.
    """
    """
    * @api {get} getPersonData Get basic info about a person
    * @apiName getPersonData
    * @apiGroup Other
    * @apiDescription This function returns an object with the person's basic info.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {String} /.gender The person's recorded gender, usually female or male. Used primarily for front-end grammar.
    * @apiSuccess {String} /.name The name of the person.
    * @apiSuccess {String} /.gov_id The person's gov_id if applicable.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getPersonData/2

    * @apiSuccessExample {json} Example response:
    {
        "gender": "female",
        "name": "Anja Bah \u017dibert",
        "gov_id": "P239"
    }
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
    """
    * @api {get} isSpeechOnDay/{?date} Check whether a speech happened on a specific day
    * @apiName isSpeechOnDay
    * @apiGroup Other
    * @apiDescription This function returns an object with the answer to the question:
      did a speech happen on a specific day? If no date is supplied it is assumed the date
      is today.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {Boolean} /.isSpeech True if a speech happened on the supplied date.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/isSpeechOnDay/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/isSpeechOnDay/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "isSpeech": false
    }
    """

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
    """
    * @api {get} isVoteOnDay/{?date} Check whether a vote happened on a specific day
    * @apiName isVoteOnDay
    * @apiGroup Other
    * @apiDescription This function returns an object with the answer to the question:
      did a vote happen on a specific day? If no date is supplied it is assumed the date
      is today.

    * @apiSuccess {Object[]} / 
    * @apiSuccess {Boolean} /.isVote True if a speech happened on the supplied date.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/isVoteOnDay/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/isVoteOnDay/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "isVote": false
    }
    """

    if date_:
        fdate = datetime.strptime(date_, settings.API_DATE_FORMAT)
    else:
        fdate = datetime.now()
    print fdate
    edate = fdate + timedelta(hours=23, minutes=59)
    votes = Vote.objects.filter(start_time__gte=fdate,
                                start_time__lte=(edate))

    return JsonResponse({"isVote": True if votes else False})


def getMPSpeechesIDs(request, person_id, date_=None):
    """Returns all speech ids of MP."""
    """
    * @api {get} getMPSpeechesIDs/{id}/{?date} Get all MP's speeches ids
    * @apiName getMPSpeechesIDs
    * @apiGroup MPs
    * @apiDescription This function returns a list of all MP's speeches up until a specific date.
      If no date is supplied it is assumed the date is today.

    * @apiSuccess {Integer[]} / List of speech ids as integers.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMPSpeechesIDs/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getMPSpeechesIDs/2/12.12.2014

    * @apiSuccessExample {json} Example response:
    [592488, 580811, 567944, 567950, 538605]
    """

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
    """
    * @api {get} getPGsSpeechesIDs/{id}/{?date} Get all PG's speeches ids
    * @apiName getPGsSpeechesIDs
    * @apiGroup PGs
    * @apiDescription This function returns a list of all PG's speeches up until a specific date.
      If no date is supplied it is assumed the date is today.

    * @apiSuccess {Integer[]} / List of speech ids as integers.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getPGsSpeechesIDs/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getPGsSpeechesIDs/2/12.12.2014

    * @apiSuccessExample {json} Example response:
    [592488, 580811, 567944, 567950, 538605]
    """

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


def getMembersWithFunction(request):
    """
    * @api {get} getMembersWithFunction/ MPs with functions in DZ
    * @apiName getMembersWithFunction
    * @apiGroup MPs
    * @apiDescription This function returns all MPs that have a function in DZ.
      That means president or vice president of the national council.

    * @apiSuccess {Integer[]} members_with_function Parladata ids of MPs with functions in DZ.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getMembersWithFunction/
    
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


def getAllQuestions(request, date_=None):
    """
    Returns array of all questions. Objects have only link with note Besedilo.
    """
    """
    * @api {get} getAllQuestions/{?date} Get all MP's questions
    * @apiName getAllQuestions
    * @apiGroup Other
    * @apiDescription This function returns all MP's questions that have been asked
      up to a specific date. If no date is supplied it is assumed the date is today.

    * @apiSuccess {Object[]} / List of Question objects.
    * @apiSuccess {String} /.recipient_text Recipient in text form as written on www.dz-rs.si.
    * @apiSuccess {Integer} /.recipient_org_id Parladata id of the organization the recipient is a member of if applicable.
    * @apiSuccess {Integer} /.recipien_id Parladata id of the recipient if applicable.
    * @apiSuccess {String} /.link URL to the relevant question document.
    * @apiSuccess {String} /.title Question title.
    * @apiSuccess {date} /.date The date on which the question was asked.
    * @apiSuccess {Integer} /.author_id The Parladata id of the MP who asked the question.
    * @apiSuccess {Integer} /.id Parladata id of the question.
    * @apiSuccess {Integer} /.session_id Parladata id of the session where this question was asked.

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getAllQuestions/
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getAllQuestions/12.12.2014
    
    * @apiSuccessExample {json} Example response:
    [
        {
            "recipient_text": "minister za infrastrukturo in prostor, ki opravlja teko\u010de posle",
            "recipient_org_id": null,
            "recipient_id": null,
            "link": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0051c03fcabad65a8c60e1ab07b2f598715f9b4384afed907db7a549169",
            "title": "v zvezi z spremenjenimi pravili za opravljanje vozni\u0161kih izpitov",
            "date": "2014-08-27T00:00:00",
            "author_id": 83,
            "id": 4973,
            "session_id": null
        }, {
            "recipient_text": "generalna sekretarka Vlade",
            "recipient_org_id": null,
            "recipient_id": null,
            "link": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005dd49e02aa5a4bdf82cd726ec231c5db754de339461cec5f929cc2f3c",
            "title": "v zvezi z glasovanjem na sejah Vlade RS",
            "date": "2014-09-10T00:00:00",
            "author_id": 78,
            "id": 4974,
            "session_id": 5618
        }, {
            "recipient_text": "ministrica za delo dru\u017eino socialne zadeve in enake mo\u017enosti",
            "recipient_org_id": null,
            "recipient_id": null,
            "link": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e00538fae5d9cbae4b468d3b346c4e28915089345234281182daa8b033fb",
            "title": "v zvezi z oskrbo starej\u0161ih",
            "date": "2014-09-26T00:00:00",
            "author_id": 23,
            "id": 4975,
            "session_id": null
        }
    ]
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
        recipient_posts = question.recipient_post.all().values('organization_id',
                                                                'membership__person_id')
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': list(recipient_person),
                 'recipient_org_id': list(recipient_org),
                 'recipient_posts': list(recipient_posts),
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
    """
    * @api {get} getBallotsCounterOfPerson/{id}/{?date} Get MP's ballot counts
    * @apiName getBallotsCounterOfPerson
    * @apiGroup MPs
    * @apiDescription This function returns a list of objects representing monthly
      ballot counts for a specific MP.

    * @apiSuccess {Object[]} / List of BalloutCounter objects.
    * @apiSuccess {Integer} /.ni Number of times the MP didn't participate in a voting event.
    * @apiSuccess {Integer} /.proti Number of times the MP voted against the motion.
    * @apiSuccess {date} /.date_ts UTF-8 date for easier sorting. The first of the month
      signifies the month in which we're counting ballots.
    * @apiSuccess {Integer} /.za Number of times the MP voted for the motion.
    * @apiSuccess {Integer} /.kvorum Number of times the MP abstained.
    * @apiSuccess {date} /.date Human-readable "Slovenian" date. The first of the month
      signifies the month in which we're counting ballots.
    * @apiSuccess {Integer} /.total Total number of ballots for this person

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getBallotsCounterOfPerson/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getBallotsCounterOfPerson/2/12.12.2014
    
    * @apiSuccessExample {json} Example response:
    [
        {
            "ni": 2,
            "proti": 3,
            "date_ts": "2014-08-01T00:00:00",
            "za": 7,
            "kvorum": 5,
            "date": "01.08.2014",
            "total": 17
        }, {
            "ni": 2,
            "proti": 8,
            "date_ts": "2014-09-01T00:00:00",
            "za": 2,
            "kvorum": 3,
            "date": "01.09.2014",
            "total": 15
        }, {
            "ni": 1,
            "proti": 1,
            "date_ts": "2014-10-01T00:00:00",
            "za": 2,
            "kvorum": 0,
            "date": "01.10.2014",
            "total": 4
        }
    ]
    """
    person = Person.objects.get(id=person_id)
    data = getBallotsCounter(person, date_=None)
    return JsonResponse(data, safe=False)


def getBallotsCounterOfParty(request, party_id, date_=None):
    """
    Api endpoint which returns ballots count of party
    """
    """
    * @api {get} getBallotsCounterOfParty/{id}/{?date} Get MP's ballot counts
    * @apiName getBallotsCounterOfParty
    * @apiGroup PGs
    * @apiDescription This function returns a list of objects representing monthly
      ballot counts for a specific PG.

    * @apiSuccess {Object[]} / List of BalloutCounter objects.
    * @apiSuccess {Integer} /.ni Number of times members of the PG didn't participate in a voting event.
    * @apiSuccess {Integer} /.proti Number of times members of the PG voted against the motion.
    * @apiSuccess {date} /.date_ts UTF-8 date for easier sorting. The first of the month
      signifies the month in which we're counting ballots.
    * @apiSuccess {Integer} /.za Number of times members of the PG voted for the motion.
    * @apiSuccess {Integer} /.kvorum Number of times members of the PG abstained.
    * @apiSuccess {date} /.date Human-readable "Slovenian" date. The first of the month
      signifies the month in which we're counting ballots.
    * @apiSuccess {Integer} /.total Total number of ballots for this person

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/getBallotsCounterOfParty/2
    * @apiExample {curl} Example with date:
        curl -i https://data.parlameter.si/v1/getBallotsCounterOfParty/2/12.12.2014
    
    * @apiSuccessExample {json} Example response:
    [
        {
            "ni": 0,
            "proti": 3,
            "date_ts": "2014-08-01T00:00:00",
            "za": 28,
            "kvorum": 3,
            "date": "01.08.2014",
            "total": 17
        }, {
            "ni": 9,
            "proti": 1,
            "date_ts": "2014-09-01T00:00:00",
            "za": 20,
            "kvorum": 0,
            "date": "01.09.2014",
            "total": 15
        }, {
            "ni": 0,
            "proti": 0,
            "date_ts": "2014-10-01T00:00:00",
            "za": 6,
            "kvorum": 2,
            "date": "01.10.2014",
            "total": 4
        }
    ]
    """
    party = Organization.objects.get(id=party_id)
    data = getBallotsCounter(party, date_=None)
    return JsonResponse(data, safe=False)


@csrf_exempt
def addQuestion(request): # TODO not documented because private refactor with security
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
        recipient_posts = [post['recipient']
                           for post
                           in recipients
                           if post['type'] == 'post']
        print session, data['naslov'], datetime.strptime(data['datum'], '%d.%m.%Y'), person, data['naslovljenec']
        if Question.objects.filter(session=session,
                                   title=data['naslov'],
                                   date=datetime.strptime(data['datum'], '%d.%m.%Y'),
                                   author=authorPerson,
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
        question.recipient_post.add(*recipient_posts)

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


def getAllChangesAfter(request, # TODO not documented because strange
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
                                'email': '',
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
        recipient_posts = question.recipient_post.all().values('organization_id',
                                                                'membership__person_id')
        q_obj = {'date': question.date,
                 'id': question.id,
                 'title': question.title,
                 'session_id': getIdSafe(question.session),
                 'author_id': getIdSafe(question.author),
                 'recipient_id': list(recipient_person),
                 'recipient_org_id': list(recipient_org),
                 'recipient_posts': list(recipient_posts),
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


def monitorMe(request): # TODO refactor name KUNST
    """Checks if API is working."""
    """
    * @api {get} monitoring Check if API is running
    * @apiName monitoring
    * @apiGroup Other
    * @apiDescription This function returns the state of the API. Either it says
      "All iz well." or it instructs you to "PANIC!"

    * @apiSuccess {String} status Either "All iz well." or it's time to "PANIC!"

    * @apiExample {curl} Example:
        curl -i https://data.parlameter.si/v1/monitoring
    
    * @apiSuccessExample {json} Example response:
    All iz well.
    """

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
        fdate = datetime.now()
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
                             'acronym': orgs[ballot.voterparty_id],
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


def getStrip(request):
    tempDate = settings.MANDATE_START_TIME.date()
    fdate = datetime.now().date()
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
    print out[keys[0]]
    outList = [{"start": 0,
                "duration": 1,
                "chars": [{'id': key,
                           'members': value} for key, value in out[keys[0]].items() if value]}]
    for key in keys:
        temp_data = [{'id': key,
                      'members': value} for key, value in out[key].items() if value]
        if temp_data == outList[-1]["chars"]:
            outList[-1]["duration"] += 1
        else:
            outList.append({"start": outList[-1]["duration"] + outList[-1]["start"],
                            "duration": 1,
                            "chars": temp_data})

    return JsonResponse(outList, safe=False)


def getMembershipNetwork(request):
    parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
    members = Membership.objects.filter(organization__in=parliamentary_group)
    fdate = datetime.now()
    members = Membership.objects.filter(Q(start_time__lte=fdate) |
                                        Q(start_time=None),
                                        Q(end_time__gte=fdate) |
                                        Q(end_time=None),
                                        organization__in=parliamentary_group)
    p_ids = members.values_list("person__id", flat=True)
    members = Membership.objects.filter(organization__in=parliamentary_group,
                                        person_id__in=p_ids)
    members = members.order_by("start_time")

    mems = {}

    for member in members:
        mems[member.person.id] = {'nodeName': member.person.name, 'group': member.organization.id, 'id': member.person.id}

    links = []
    visited = []
    for m_id in mems.keys():
        current = members.filter(person_id=m_id)
        for c_m in current:
            visited.append(c_m.id)
            others = members.filter(organization_id=c_m.organization_id).exclude(id__in=visited)
            for o_m in others:
                days = getDaysTogether(c_m, o_m)
                if days:
                    links.append({'source': c_m.person_id,
                                  'target': o_m.person_id,
                                  'value': days})

    temp_links = {}
    out = []
    for link in links:
        key = str(link['source'])+'_'+str(link['target'])
        if key in temp_links.keys():
            temp_links[key]['value'] += link['value']
        else:
            temp_links[key] = link

    nodes = []
    ids = {}
    idx = 0
    for m in mems.keys():
        nodes.append(mems[m])
        ids[m] = idx
        idx += 1

    links = []
    for link in temp_links.values():
        links.append({'source': ids[link['source']],
                      'source_id': link['source'],
                      'target': ids[link['target']],
                      'target_id': link['target'],
                      'value': link['value']})

    return JsonResponse({'nodes': nodes,
                         'links': links})


def getDaysTogether(p1, p2):
    return has_overlap(setDateIfNone(p1.start_time, 'start'),
                       setDateIfNone(p1.end_time, 'end'),
                       setDateIfNone(p2.start_time, 'start'),
                       setDateIfNone(p2.end_time, 'end'))


def has_overlap(A_start, A_end, B_start, B_end):
    latest_start = max(A_start, B_start)
    earliest_end = min(A_end, B_end)
    if latest_start <= earliest_end:
        return (earliest_end - latest_start).days
    else:
        return 0


def setDateIfNone(date, type_='start'):
    if not date:
        if type_ == 'start':
            return datetime(day=1, month=8, year=2014)
        elif type_ == 'end':
            return datetime.now()
    return date
