# -*- coding: utf-8 -*-
from parladata.models import *
import numpy
from django.db.models import Q
from datetime import datetime, timedelta
import requests
from django.conf import settings

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