# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from parladata.models import Person, Membership, Organization
from datetime import datetime
sklici = {'6':{'start_time': datetime(day=21, month=12, year=2011),
               'end_time': datetime(day=1, month=8, year=2014),
               'nep_wo': datetime(day=2, month=8, year=2014),},
          '5':{'start_time': datetime(day=2, month=10, year=2008),
               'end_time': datetime(day=21, month=10, year=2011),
               'nep_wo': datetime(day=22, month=10, year=2011)}}

parser_vars = {'6': {'member_class': ' width: 216px;',
                     'pg_class': ' width: 652px;',
                     'table_search': {'dir':"ltr"}},
               '5': {'member_class': ' width: 140px;',
                     'pg_class': ' width: 653px;',
                     'table_search': {'style':" width: 796px;"}}}



def add_membership(name, parties, sklic=6):
    person = find_person(name)
    for i in parties:
        print "input: ", name, i
        #organization = Organization.objects.filter(name_parser__icontains=i)
        organization = find_org(i, name)
        print person, name, organization
        """
        if organization.classification == 'nepovezani poslanec' or organization._acronym == 'NP':
            Membership(person = person[0],
                       organization=organization,
                       start_time=sklici[str(sklic)]['nep_wo'],
                       end_time=None,
                       role='član',
                       label='cl').save()
        else:
            Membership(person = person[0],
                       organization=organization,
                       start_time=sklici[str(sklic)]['start_time'],
                       end_time=sklici[str(sklic)]['end_time'],
                       role='član',
                       label='cl').save()
        """


def parse_memberships(url, sklic):
    html_doc = requests.get(url)
    soup = BeautifulSoup(html_doc.content, 'html.parser')

    i=0

    poslanci = []
    stranke = []
    for i, mp in enumerate(soup.find_all('table', **parser_vars[str(sklic)]['table_search'])[0].find_all(style=parser_vars[str(sklic)]['member_class'])):
        if i > 0:
            # preprocessing here
            poslanci.append(mp.string)

    for pg in soup.find_all('table', **parser_vars[str(sklic)]['table_search'])[0].find_all(style=parser_vars[str(sklic)]['pg_class']):
        # preprocessing here
        stranke.append(pg.string.split(', prej '))

    data = zip(poslanci, stranke)

    for line in data:
        add_membership(*line, sklic=sklic)

def find_org(name_parser, person_name):
    if 'dr. ' in person_name:
        person_name = person_name[4:]
    elif 'mag. ' in person_name:
        person_name = person_name[5:]
    if name_parser == 'PNeP':
        name_parser = 'NP'
    elif name_parser == 'NeP':
        name_parser = 'NeP - ' + ''.join(reversed([name[0] for name in person_name.split(' ')]))
        print 'NEP ', name_parser
    elif name_parser in ['ITAL. NAR. SK.', 'MAD. NAR. SK.']:
        name_parser = 'NS'
    organizations = Organization.objects.filter(name_parser__icontains=name_parser)
    for organization in organizations:
        if name_parser in organization.name_parser.split(','):
            return organization
    print '______________________________', person_name
    return None


def find_person(name_parser):
    if 'dr. ' in name_parser:
        name_parser = name_parser[4:]
    elif 'mag. ' in name_parser:
        name_parser = name_parser[5:]
    person = Person.objects.filter(name_parser__icontains=name_parser.strip())
    if len(person)>1:
        print "TUKI NEKI NI OK"
    return person

parse_memberships("https://www.dz-rs.si/wps/portal/Home/ODrzavnemZboru/Dogodki/20obletnicaDrzavnegazbora/bee07e17-39db-4caa-935b-92e8f781828b/!ut/p/z1/tVRLU8IwEP4reOBYs0lf6bGA1gKlI22F5uL0EbBqE8QKyq83Mo7jYxAch1wymf0eu8luEENTxES2quZZU0mR3atzyqzrzmhs-gMPQ9ihBPxxEJk9Y4R9z0KTLWDgh5HTwS54Y0MB8MCJh8EQgwKwL-Ez3FPhwL_wRy4BwN_5oYPPwU90z9CDGCAgh_Fhx3Jhy__InzqOBW7Uv0yuuqBDz3zn_wJgf6r_a_4ePdB_V_0J2ce_QgyxQjSL5gal5aZVyuKp5qJ5bINslctNthK8bm1yuXxqQynnsryr2kDgtCXze96IqsjakHMONse2pjtlrhlFlmmObuaaQzid2RRTQvM3n0VRlSg9CD3Z1zjs92dLFd_eyacGmqwqvkaJkMta9Wn0x_QufjhQ6lrKIR4a59ElUTf0T4dv8jCw3wqIeyQMOzp4xnHlrePKm8eVt_8p3983tepbI8ugG8yVbNbcaJWYSTQ9SFtRq9uHB-aqsZOi4c8Nmh517hZ1sl011V-0tL9ar-NZ3c3pp21CH92TV0q17Hw!/dz/d5/L2dBISEvZ0FBIS9nQSEh/", 5)