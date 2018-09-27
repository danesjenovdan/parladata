# -*- coding: utf-8 -*-
from parladata.models import *

from datetime import datetime

import requests
mandate_start_time = '2015-10-25'
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
                mandates = len([1 for i in mp['data']['sejm_mps.history'].split(' ') if i == 'poseł']) + 1
                person = Person(
                    name=mp['data']['sejm_mps.name'],
                    name_parser=mp['data']['sejm_mps.name'],
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
                person.districts.add(district)


                if mp['sejm_mps.date_oath']:
                    start_time = parse_date(mp['sejm_mps.date_oath'])
                elif mp['sejm_mps.date_elected']:
                    start_time = parse_date(mp['sejm_mps.date_elected'])
                else:
                    start_time = parse_date(mandate_start_time)

                if mp['sejm_mps.date_expiry']:
                    end_time = parse_date(mp['sejm_mps.date_expiry'])
                else:
                    end_time = None

                add_membership(person, sejm, org, 'voter', start_time, end_time)
                add_membership(person, org, None, 'member', start_time, end_time)





def add_or_get_party(obj):
    org = Organization.objects.filter(gov_id=obj['data']['sejm_clubs.id'])
    if not org:
        org = Organization(
            _name=obj['data']['sejm_clubs.name'],
            name_parser='',
            _acronym=obj['data']['sejm_clubs.id'],
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

def add_or_get_area(obj):
    area = Area.objects.filter(name=obj['data']['sejm_mps.constituency_name'])
    if not area:
        org = Area(
            name=obj['data']['sejm_mps.constituency_name'],
            classification='district',
            )
        org.save()
    else:
        area = area[0]
    return area



def read_data_from_api(url, per_page = None):
    end = False
    page = 1
    print(url)
    while not end:
        print(page)
        response = requests.get(url).json()
        yield response['Dataobject']
        if 'next' not in response['Links'].keys():
            print('generator end')
            break
        url = response['Links']['next']

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')