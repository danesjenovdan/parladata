# -*- coding: utf-8 -*-
from parladata.models import *
import numpy
from django.db.models import Q
from datetime import datetime, timedelta, date
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from collections import Counter

#returns average from list of integers
def AverageList(list):
    return sum(list) / float(len(list))

#returns average from dictionary of integers
def AverageListOfDic(list, key):
    data = [i[key] for i in list]
    return sum(data) / float(len(list))

#returns maximum of list of dictionaries
def MaxListOfDic(list, key):
    data = [i[key] for i in list]
    return max(data)

'''
MP = Members of parlament
#Function: git config
'''
# getMPObject return objects of all parlament members
def getMPObjects(date_=None):
    if not date_:
        date_ = datetime.now()
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    members = members.filter(Q(start_time__lte=date_)|Q(start_time=None), Q(end_time__gte=date_)|Q(end_time=None))
    return [i.person for i in members]


def getCurrentMandate():
    return Mandate.objects.all()[-1]


def getVotesDict(date=None):
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    votes = dict()
    # balotFromMandat = Ballot.objects.filter('vote__session__mandate' = getCurrentMandate())

#   with open('/Users/muki/Desktop/testis.csv', 'w') as f:
    for m in list(set(members.values_list("person", flat=True))):
        print m
#           for b in Ballot.objects.filter(voter=m):
#               f.write(str(b.option) + ',' + str(b.vote.id) + ',' + str(b.id))
#               f.write('\n')

        if date:
            ballots = list(Ballot.objects.filter(voter__id=m, vote__start_time__lte=datetime.strptime(date, settings.API_DATE_FORMAT).date()).order_by('vote__start_time').values_list('option', 'vote_id'))
        else:
            ballots = list(Ballot.objects.filter(voter__id=m).order_by('vote__start_time').values_list('option', 'vote_id'))
    
        if ballots:
            votes[str(m)] = {ballot[1]: ballot[0] for ballot in ballots}
        #Work around if ther is no ballots for member
        else:
            votes[str(m)] = {}

        if m==6:
            print votes[str(m)]
        print votes.keys()
#   f.close()
    print votes.keys()
    return votes

def voteToLogical(vote):
    if vote=="za":
        return 1
    elif vote=="proti":
        return 0
    else :
        return -1

def votesToLogical(votes, length):
    maxVotes = length
    for key in votes.keys():
        votes[key] = map(voteToLogical, votes[key])

        #remove this when numbers of ballots are equals for each member
        if (len(votes[key]) < length):
            votes[key].extend(numpy.zeros(maxVotes-int(len(votes[key]))))
        else:
            votes[key] = [votes[key][i] for i in range(length)]

#doesn't save
#TODO use the right majority for the votes
def fillVoteResult():
    ballots = getVotesDict()
    votesToLogical(ballots, len(Vote.objects.all()))
    votes = Vote.objects.all().order_by('id')

    for i in Vote.objects.all().values_list('id', flat=True):
        suma = 0
        for p in ballots.items():
            try:
                suma = suma + p[1][i]
            except:
                print "ni enako :D"
        print type(votes[i].result)
        if suma > len(ballots.keys())/2:

            votes[i].result = "da"
        else:
            votes[i].result = "ne"
        votes[i].save()


def makeVoteResults():
    votes = Vote.objects.all()

    for vote in votes:
        za = vote.ballot_set.filter(option='za')
        proti = vote.ballot_set.filter(option='proti')
        kvorum = vote.ballot_set.filter(option='kvorum')

        print len(za), len(proti), len(kvorum), vote.result

        if kvorum < 45:
            vote.result = 'ni kvoruma'
            vote.save()
        else:
            if len(za) > len(proti):
                vote.result = 'yes'
                vote.save()
            else:
                vote.result = 'no'
                vote.save()


def getPMMemberships():
    f = open('memberships.tsv', 'w')
    f.write("person\tmember of\trole\n")
    for p in Person.objects.all():
        for m in Membership.objects.filter(person=p):
            f.write(p.name.encode("utf-8")+"\t ")
            f.write(m.organization.name.encode("utf-8")+"\t ")
            try:
                if m.role == "":
                    f.write("NONE\t")
                else:
                    f.write(m.role+"\t ")
            except:
                f.write("NONE\t ")

            f.write("\n")


def checkNumberOfMembers():
    import csv
    with open('members_on_day.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        d = datetime(year=2014, day=1, month=8)
        day = timedelta(days=1)
        for i in range(700):
            g = requests.get("https://data.parlameter.si/v1/getMembersOfPGsAtDate/"+d.strftime(settings.API_DATE_FORMAT)).json()
            csvwriter.writerow([d.strftime(settings.API_DATE_FORMAT), str(sum([len(g[g_]) for g_ in g]))])
            d=d+day


def checkNumberOfMembers1():
    import csv
    with open('members_on_day.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        r = requests.get("http://localhost:8000/v1/getMembersOfPGsRanges/05.05.2016").json()
        for g in r:
            csvwriter.writerow([g["start_date"], str(sum([len(g["members"][g_]) for g_ in g["members"]]))])


#function for finding MPs membersihp date issues
def getFails():
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    members = members.filter()
    start = Vote.objects.all().order_by("start_time")[0].start_time
    out = {}
    for member in members:
        if member.start_time==None and member.end_time==None:
            votes=Vote.objects.filter(Q(start_time__gte=start)|Q(end_time__lte=datetime.now()))
        elif member.start_time==None and member.end_time!=None:
            votes=Vote.objects.filter(Q(start_time__gte=start)|Q(end_time__lte=member.end_time))
        elif member.start_time!=None and member.end_time!=None:
            votes=Vote.objects.filter(Q(start_time__gte=member.start_time)|Q(end_time__lte=member.end_time))
        elif member.start_time!=None and member.end_time==None:
            votes=Vote.objects.filter(Q(start_time__gte=member.start_time)|Q(end_time__lte=datetime.now()))
        for vote in votes:
            if not Ballot.objects.filter(voter=member.person, vote=vote):
                if member.person.id in out.keys():
                    out[member.person.id].append(vote.start_time)
                else:
                    out[member.person.id]= [vote.start_time]
    print out


def getMembershipDuplications1(requests):
    # prepare data
    start_date = date(day=1, month=9, year=2014)
    end_date = date.today()
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))

    data = []

    #for i in range((end_date-start_date).days):
    for i in range(10):
        print i
        date_ = start_date + timedelta(days=i)
        print date_
        members = Membership.objects.filter(organization__in=parliamentary_groups)

        members = members.filter(Q(start_time__lte=date_)|Q(start_time=None), Q(end_time__gte=date_)|Q(end_time=None))

        member_ids = members.values_list("person__id", flat=True)
        conf_members = set([member for member in member_ids if list(member_ids).count(member)>1])
        data.append({"persons":[{member: [{"membership_id": membership.id, "org_id": membership.organization.id} for membership in members.filter(person_id=member)] } for member in conf_members]})


        #org_ids = members.values_list("organization__id", flat=True)
        #data[date_.strftime(settings.API_DATE_FORMAT)].update({"groups": [{org:  list(members.filter(organization__id=org).values_list("role", flat=True)) } for org in org_ids]})

    context = {}
    out = []
    first_date=start_date.strftime(settings.API_DATE_FORMAT)
    last_day = None
    for day in data:
        if last_day and day["persons"]==last_day["persons"]:
            continue
        else:
            if last_day:
                for person in last_day["persons"]:
                    out.append({"od": first_date, "do": last_day["date"], "person": person})
                first_date= day["date"]
            last_day = day

    for person in last_day["persons"]:
        out.append({"od": first_date, "do": last_day["date"], "person": person})
            

    context["data"] = out

    print out

    return render(requests, "debug_memberships.html", context)

def getMembershipDuplications(requests):
    # prepare data
    context = {}
    start_time = datetime(day=1, month=9, year=2014)
    end_time = datetime.now()
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))

    data = []

    members = Membership.objects.filter(organization__in=parliamentary_groups)
    
    #members = members.filter(Q(start_time__lte=date_)|Q(start_time=None), Q(end_time__gte=date_)|Q(end_time=None))
    out = []
    checked = []
    for membership in members:

        mem_start = membership.start_time if membership.start_time else start_time
        mem_end = membership.end_time if membership.end_time else end_time
        checked.append(membership.id)

        for chk_mem in members.filter(person=membership.person).exclude(id__in=checked):

            chk_start = chk_mem.start_time if chk_mem.start_time else start_time
            chk_end = chk_mem.end_time if chk_mem.end_time else end_time

            if chk_start < mem_start:
                #preverji da je chk_mem pred membershipom
                if chk_end > mem_start:
                    #FAIL
                    out.append({"member": membership.person, "mem1": membership, "mem2": chk_mem})

            elif chk_start > mem_start:
                #preverji da je chk_mem pred membershipom
                if mem_end > chk_start:
                    #FAIL
                    out.append({"member": membership.person, "mem1": membership, "mem2": chk_mem})

            else:
                print "WTF enaka sta?"

    context["data"] = out

    #check if one person have more then one membership per organization
    members_list = list(members.values_list("person", flat=True))
    org_per_person=[]
    for member in members_list:
        temp = dict(Counter(list(members.filter(person__id=member).values_list("organization", flat=True))))
        print temp
        for key, val in temp.items():
            if val>1:
                org_per_person.append({"member": Person.objects.get(id=member), 
                                       "organization": Organization.objects.get(id=key), 
                                       "mem1": list(Membership.objects.filter(person__id=member, organization__id=key))[0],
                                       "mem2": list(Membership.objects.filter(person__id=member, organization__id=key))[1]})

        context["orgs_per_person"] = org_per_person



    return render(requests, "debug_memberships.html", context)