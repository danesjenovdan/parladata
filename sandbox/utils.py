# -*- coding: utf-8 -*-
from parladata.models import Membership, Person
import csv
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.db.models import Q


def getPMMemberships():
    f = open('memberships.tsv', 'w')
    f.write("person\tmember of\trole\n")
    for p in Person.objects.all():
        for m in Membership.objects.filter(person=p):
            f.write(p.name.encode("utf-8") + "\t ")
            f.write(m.organization.name.encode("utf-8") + "\t ")
            try:
                if m.role == "":
                    f.write("NONE\t")
                else:
                    f.write(m.role + "\t ")
            except:
                f.write("NONE\t ")

            f.write("\n")


def checkNumberOfMembers():
    with open('members_on_day.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        d = datetime(year=2014, day=1, month=8)
        day = timedelta(days=1)
        for i in range(700):
            g = requests.get("https://data.parlameter.si/v1/getMembersOfPGsAtDate/" + d.strftime(settings.API_DATE_FORMAT)).json()
            csvwriter.writerow([d.strftime(settings.API_DATE_FORMAT), str(sum([len(g[g_]) for g_ in g]))])
            d = d + day


def checkNumberOfMembers1():
    with open('members_on_day.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

        r = requests.get("http://localhost:8000/v1/getMembersOfPGsRanges/05.05.2016").json()
        for g in r:
            csvwriter.writerow([g["start_date"], str(sum([len(g["members"][g_]) for g_ in g["members"]]))])


def checkMinistersParser():
    with open('ministers.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['recipient_text', 'recipient_person', 'recipient_organization'])
        mv = Organization.objects.filter(classification__in=['vlada',
                                                             'ministrstvo',
                                                             'sluzba vlade',
                                                             'urad vlade'])

        for q in qq:
            date_of = q.date
            csvwriter.writerow([q.recipient_text,
                                [{'name': p.name, 'org': Post.objects.filter(Q(start_time__lte=date_of) |
                                                                             Q(start_time=None),
                                                                             Q(end_time__gte=date_of) |
                                                                             Q(end_time=None),
                                                                             organization__in=mv,
                                                                             membership__person=p).values_list('organization__name')} for p in q.recipient_person.all()],
                                q.recipient_organization.all().values_list("name")]