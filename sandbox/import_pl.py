# -*- coding: utf-8 -*-
from django.utils.html import strip_tags

from parladata.models import *

from datetime import datetime
from pyquery import PyQuery as pq

import requests
import time
import unicodedata


mandate_start_time = '2015-10-25'

# MEMBERS

members = {p.name_parser: p for p in  Person.objects.all() if p.name_parser}
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
        response = tryHard(url).json()
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


def get_od_add_speaker_by_name(name_str):
    person = Person.objects.filter(name__icontains=name_str)
    if person:
        return person[0]
    else:
        print "ADDING PERSON " + name_str
        person = Person(
            name=name_str,
            )
        person.save()
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
        debate_data = tryHard('https://api-v3.mojepanstwo.pl/dane/sejm_debates/' + debate).json()
        import_debate(debate_data, session, agenda_item)

    for motion_id in data['data']['sejm_agenda_items.voting_id']:
        if not Motion.objects.filter(gov_id=motion_id):
            motion_data = tryHard('https://api-v3.mojepanstwo.pl/dane/sejm_votings/' + motion_id + '.json?layers[]=votes').json()
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
        if agenda_item not in debate.agenda_item.all():
            debate.agenda_item.add(agenda_item)
        return
    else:
        debate = Debate(
            order=data['data']['sejm_debates.ord'],
            date=parse_date(data['data']['sejm_days_speeches.date']),
            session=session,
            gov_id=data['id']
            )
        debate.save()
        debate.agenda_item.add(agenda_item)
    for page in read_data_from_api('https://api-v3.mojepanstwo.pl/dane/sejm_speeches?conditions[sejm_speeches.debate_id]='+data['id']):
        for speech in page:
            content = tryHard('https://sejmometr.pl/api/wystapienia/'+speech['id']+'.html').content

            splited_contents = parse_speech_content(speech)
            for splited in splited_contents:
                Speech(
                    speaker=splited['person'],
                    #party=,
                    content=splited['text'],
                    order=splited['order'],
                    session=session,
                    start_time=parse_date(speech['data']['sejm_sittings_days.date']),
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


def tryHard(url):
    data = None
    counter = 0
    while not data:
        try:
            data = requests.get(url)
        except:
            print(data.status_code, counterm, url)
            #counter += 1
            time.sleep(5)
            pass
        if not data:
            print(data.status_code, counterm, url)
            time.sleep(5)
            counter += 1
        
        if counter > 5:
            print 'SHITT'
            return None
    return data


def parse_speech_content(data):
    def get_and_increase_order(order):
        prev = order['value']
        order['value']+=1
        return prev
    # this dont work yet
    #content = data['data']['sejm_speeches.html']
    content = tryHard('https://sejmometr.pl/api/wystapienia/'+data['id']+'.html').text
    print content
    d = pq(content)

    order = {'value': int(data['data']['sejm_speeches.ord']) * 100}

    person = get_or_add_speaker(data)
    out = []
    c_str = []

    for i in d("p"):
        p = pq(i)
        
        text = p.text()
        # text = unicodedata.normalize('NFC', unicode(p.text()))
        print text
        if p.hasClass("opis") or text.startswith('(Poseł'.decode("utf-8")) or text.startswith('(Głos z sali'.decode("utf-8")):

            # if injected speech
            if c_str:
                out.append({'text': ' '.join(c_str), 'person': person, 'order': get_and_increase_order(order)})

                c_str = []
            text = text.strip("()").split(':')
            if len(text) == 2:
                print 'Poseł'.decode("utf-8"), text[0]
                if 'Poseł'.decode("utf-8") in text[0]:
                    op_person = get_od_add_speaker_by_name(text[0][7:].strip())
                    out.append({'text': text[1].strip(), 'person': op_person, 'order': get_and_increase_order(order)})
                else:
                    op_person = get_od_add_speaker_by_name(text[0].strip())
                    out.append({'text': text[1].strip(), 'person': op_person, 'order': get_and_increase_order(order)})
        else:
            c_str.append(text)

    if c_str:
        out.append({'text': ' '.join(c_str), 'person': person, 'order': get_and_increase_order(order)})

    return out

