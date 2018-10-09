# -*- coding: utf-8 -*-
from django.utils.html import strip_tags

from parladata.models import *

from datetime import datetime

import requests
mandate_start_time = '2015-10-25'

# MEMBERS

members = {p.name_parser: p for p in  Person.objects.all()}
options = {
    '1' : 'for',
    '2': 'against',
    '3': 'abstain',
    '4': 'absent'
    }

def import_mps():
    sejm = Organization.objects.get(_name='Sejm')
    for page in read_data_from_api('https://api-v3.mojepanstwo.pl/dane/sejm_mps'):
        for mp in page:
            print mp
            if Person.objects.filter(gov_id=mp['id']):
                continue
            else:
                org = add_or_get_party(mp)
                district = add_or_get_district(mp)
                mandates = len([1 for i in mp['data']['sejm_mps.history'].encode("utf8").split(' ') if i == 'poseł']) + 1
                person = Person(
                    name=mp['data']['sejm_mps.name'],
                    name_parser=mp['data']['sejm_mps.id'],
                    previous_occupation=mp['data']['sejm_mps.history'],
                    family_name=mp['data']['sejm_mps.last_name'],
                    given_name=mp['data']['sejm_mps.first_name'],
                    birth_date=parse_date(mp['data']['sejm_mps.date_birthday']),
                    gov_id=mp['data']['sejm_mps.id'],
                    additional_name=mp['data']['sejm_mps.second_name'],
                    voters=mp['data']['sejm_mps.election_votes_count'],
                    education=mp['data']['sejm_mps.occupation'],
                    education_level=mp['data']['sejm_mps.education'],
                    email=mp['data']['sejm_mps.email'],
                    gender='male' if mp['data']['sejm_mps.sex'] == 'M' else 'female',
                    mandates=mandates,
                    )
                person.save()
                person.districts.add(district.id)


                if mp['data']['sejm_mps.date_oath']:
                    start_time = parse_date(mp['data']['sejm_mps.date_oath'])
                elif mp['data']['sejm_mps.date_elected']:
                    start_time = parse_date(mp['data']['sejm_mps.date_elected'])
                else:
                    start_time = parse_date(mandate_start_time)

                if mp['data']['sejm_mps.date_expiry']:
                    end_time = parse_date(mp['data']['sejm_mps.date_expiry'])
                else:
                    end_time = None

                add_membership(person, sejm, org, 'voter', start_time, end_time)
                add_membership(person, org, None, 'member', start_time, end_time)





def add_or_get_party(obj):
    if obj['data']['sejm_mps.club_id']:
        org = Organization.objects.filter(gov_id=obj['data']['sejm_clubs.id'])
    else:
        org = Organization.objects.filter(gov_id=-1)
    if not org:
        org = Organization(
            _name=obj['data']['sejm_clubs.name'],
            name_parser='',
            _acronym=obj['data']['sejm_clubs.name_short'],
            gov_id=obj['data']['sejm_clubs.id'],
            classification='pg',
            )
        org.save()
    else:
        org = org[0]
    return org

#TODO
def add_membership(person, organization, on_behalf_of, role, start_time, end_time):
    Membership(
        organization=organization,
        on_behalf_of=on_behalf_of,
        role=role,
        person=person,
        start_time=start_time,
        end_time=end_time,
        ).save()
    pass

def add_or_get_district(obj):
    try:
        area = Area.objects.get(name=obj['data']['sejm_mps.constituency_name'])
    except:
        area = Area(
            name=obj['data']['sejm_mps.constituency_name'],
            calssification='district',
            )
        area.save()
    return area



def read_data_from_api(url, per_page = None):
    end = False
    page = 1
    while not end:
        response = requests.get(url).json()
        yield response['Dataobject']
        if 'next' not in response['Links'].keys():
            break
        url = response['Links']['next']

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def parse_datetime(time_str):
    return datetime.strptime(time_str, '%Y-%m-%d %X')


def get_or_add_speaker(data):
    try:
        person = members[data['data']['sejm_speakers.id']]
    except:
        print('adding visitor ', data['data']['sejm_speakers.name'])
        person = Person(
            name=data['data']['sejm_speakers.name'],
            name_parser=data['data']['sejm_speakers.id']
            )
        person.save()
        members[data['data']['sejm_speakers.id']] = person
    return person


# SESSIONS

def import_sessions():
    sejm = Organization.objects.get(_name='Sejm')
    for page in read_data_from_api('https://api-v3.mojepanstwo.pl/dane/sejm_sittings/'):
        for item in page:
            print('adding session', item['data']['sejm_sittings.number'])
            session = Session.objects.filter(gov_id=item['data']['sejm_sittings.id'])
            if session:
                session = session[0]
            else:
                session = Session(
                    name=item['data']['sejm_sittings.number'],
                    gov_id=item['data']['sejm_sittings.id'],
                    organization=sejm,
                    )
                session.save()
                session.organizations.add(sejm)

            for page in read_data_from_api('https://api-v3.mojepanstwo.pl/dane/sejm_agenda_items?conditions[sejm_agenda_items.sitting_id]=' + item['data']['sejm_sittings.id']):
                for item in page:
                    import_agenda_item(item, session)





def import_agenda_item(data, session):
    agenda_item = AgendaItem.objects.filter(gov_id=data['id'])
    if agenda_item:
        agenda_item = agenda_item[0]
    else:
        agenda_item = AgendaItem(
            gov_id=data['id'],
            name=data['data']['sejm_agenda_items.title'],
            session=session,
        )
        agenda_item.save()
        print('adding agneda item', data['data']['sejm_agenda_items.title'])

    for debate in data['data']['sejm_agenda_items.debate_id']:
        debate_data = requests.get('https://api-v3.mojepanstwo.pl/dane/sejm_debates/' + debate).json()
        import_debate(debate_data, session, agenda_item)

    for motion_id in data['data']['sejm_agenda_items.voting_id']:
        motion_data = requests.get('https://api-v3.mojepanstwo.pl/dane/sejm_votings/' + motion_id + '.json?layers[]=votes').json()
        motion = Motion(
            text=motion_data['data']['sejm_votings.title'],
            session=session,
            result=get_result(motion_data['data']['sejm_votings.result']),
            gov_id=motion_data['id'],
            agenda_item=agenda_item,
        )
        motion.save()

        vote = Vote(
            motion=motion,
            session=session,
            name=motion_data['data']['sejm_votings.title'],
            result=get_result(motion_data['data']['sejm_votings.result']),
            start_time=parse_datetime(motion_data['data']['sejm_votings.time']),
        )
        vote.save()
        for ballot_ in motion_data['layers']['votes']:
            Ballot(
                vote=vote,
                voter=members[ballot_['mp_id']],
                option=options[ballot_['vote_id']]
            ).save()


def import_debate(data, session, agenda_item):
    debate = Debate.objects.filter(gov_id=data['id'])
    if debate:
        debate = debate[0]
        return
    else:
        debate = Debate(
            order=data['data']['sejm_debates.ord'],
            date=parse_date(data['data']['sejm_days_speeches.date']),
            agenda_item=agenda_item,
            session=session,
            gov_id=data['id']
            )
        debate.save()
    for page in read_data_from_api('https://api-v3.mojepanstwo.pl/dane/sejm_speeches?conditions[sejm_speeches.debate_id]='+data['id']):
        for speech in page:
            content = strip_tags(requests.get('https://sejmometr.pl/api/wystapienia/'+speech['id']+'.html').content)
            Speech(
                speaker=get_or_add_speaker(speech),
                #party=,
                content=content,
                order=speech['data']['sejm_speeches.ord'],
                session=session,
                start_time=debate.date,
                agenda_item=agenda_item,
                valid_from=debate.date,
                valid_to=datetime.max,
                debate=debate
            ).save()



def get_result(text):
    if text == 'against':
        return 0
    elif text == 'for':
        return 1
    else:
        return -1
