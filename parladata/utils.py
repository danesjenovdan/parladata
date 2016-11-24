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
import csv
from django.utils.encoding import smart_str
import json
import requests
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
    #for m in [person.id for person in members]:
    for m in list(set(members.values_list("person", flat=True))):
        print m
#           for b in Ballot.objects.filter(voter=m):
#               f.write(str(b.option) + ',' + str(b.vote.id) + ',' + str(b.id))
#               f.write('\n')

        if date:
            date2 = datetime.strptime(date, settings.API_DATE_FORMAT) + timedelta(days=1) - timedelta(seconds=1)
            ballots = list(Ballot.objects.filter(voter__id=m, vote__start_time__lte=date2).order_by('vote__start_time').values_list('option', 'vote_id'))
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
    #for key in votes.keys():
    #    if not votes[key]:
    #        votes.pop(key)
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


def getMembershipDuplications1(request):
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

    return render(request, "debug_memberships.html", context)

def getMembershipDuplications(request):
    # prepare data
    context = {}
    start_time = datetime(day=1, month=8, year=2014)
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

            if chk_start <= mem_start:
                #preverji da je chk_mem pred membershipom
                if chk_end >= mem_start:
                    #FAIL
                    out.append({"member": membership.person, "mem1": membership, "mem2": chk_mem})

            elif chk_start >= mem_start:
                #preverji da je chk_mem pred membershipom
                if mem_end >= chk_start:
                    #FAIL
                    out.append({"member": membership.person, "mem1": membership, "mem2": chk_mem})

            else:
                print "WTF enaka sta?"

    context["data"] = out

    #check if one person have more then one membership per organization
    members_list = list(members.values_list("person", flat=True))
    org_per_person=[]
    added_mems = []
    for member in members_list:
        temp = dict(Counter(list(members.filter(person__id=member).values_list("organization", flat=True))))
        print temp
        for key, val in temp.items():
            if val>1 and not Membership.objects.filter(person__id=member, organization__id=key)[0].id in added_mems:
                print val
                added_mems.append(Membership.objects.filter(person__id=member, organization__id=key)[0].id)
                org_per_person.append({"member": Person.objects.get(id=member), 
                                       "organization": Organization.objects.get(id=key), 
                                       "mem1": list(Membership.objects.filter(person__id=member, organization__id=key))[0],
                                       "mem2": list(Membership.objects.filter(person__id=member, organization__id=key))[1]})

    context["orgs_per_person"] = org_per_person

    context["roles"] = []
    orgs = members.values_list("organization", flat=True)
    orgs = list(set(list(members.values_list("organization", flat=True))))
    for org in orgs:
        org_ = Organization.objects.get(id=org)
        posts = [membership.memberships.all().values_list("role", flat=True) for membership in org_.memberships.all()]
        roles = dict(Counter([role for post in posts for role in post]))
        context["roles"].append({"org": org_, "roles": [{"role": role, "count": count}for role, count in roles.items()]})


    context["count_of_persons"] = []
    pgRanges = requests.get("https://data.parlameter.si/v1/getMembersOfPGsRanges/"+datetime.now().strftime("%d.%m.%Y")).json()
    for pgRange in pgRanges:
        count = len([member for pg in pgRange["members"].values() for member in pg])
        members_ids = [member for pg in pgRange["members"].values() for member in pg]
        context["count_of_persons"].append({"count": {"count": count, "start_date": pgRange["start_date"], "end_date": pgRange["end_date"]}, "members": [member for pg in pgRange["members"].values() for member in pg]})
        if len(context["count_of_persons"])>1:
            context["count_of_persons"][-1]["added"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else ""} for x in context["count_of_persons"][-1]["members"] if x not in context["count_of_persons"][-2]["members"]]
            context["count_of_persons"][-1]["removed"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, end_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, end_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M")) else None} for x in context["count_of_persons"][-2]["members"] if x not in context["count_of_persons"][-1]["members"]]
            context["allMps"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else x} for x in context["count_of_persons"][-1]["members"]]
        else:
            context["count_of_persons"][-1]["added"] = [{"name": Person.objects.get(id=x).name, "person_id": x} for x in context["count_of_persons"][-1]["members"]]


    context["voters_counts"] = []
    person_ids = set(list(members.values_list("person", flat=True)))
    for person in person_ids:
        prs = Person.objects.get(id=person)
        if prs.voters == None or prs.voters == 0:
            context["voters_counts"].append(prs)




    #membership duration vs. post duration
    context["post_dupl"] = []
    members = Membership.objects.all()
    for membership in members:
        posts = membership.memberships.all()

        mem_start = membership.start_time
        mem_end = membership.end_time

        start_time = datetime(day=1, month=8, year=2014)
        end_time = datetime.now()

        checked = []
        print "count postov", posts.count()
        for post in posts:
            post_start = post.start_time if post.start_time else start_time
            post_end = post.end_time if post.end_time else end_time
            checked.append(post.id)
            for chk_post in posts.exclude(id__in=checked):
                print post
                print chk_post
                chk_start = chk_post.start_time if chk_post.start_time else start_time
                chk_end = chk_post.end_time if chk_post.end_time else end_time
                #check here
                if chk_start < post_start:
                    #preverji da je chk_mem pred membershipom
                    if chk_end > post_start:
                        #FAIL
                        context["post_dupl"].append({"member": post.membership.person, "post1": post, "post2": chk_post})

                elif chk_start > post_start:
                    #preverji da je chk_mem pred membershipom
                    if post_end > chk_start:
                        #FAIL
                        context["post_dupl"].append({"member": post.membership.person, "post1": post, "post2": chk_post})

                if chk_start == post_start:
                    context["post_dupl"].append({"member": post.membership.person, "post1": post, "post2": chk_post})
                elif chk_end == post_end:
                    context["post_dupl"].append({"member": post.membership.person, "post1": post, "post2": chk_post})

    print context["post_dupl"]

    return render(request, "debug_memberships.html", context)


def getBlindVotes():
    # prepare data
    context = {}
    start_time = datetime(day=1, month=8, year=2014)
    end_time = datetime.now()
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))

    data = []

    members = Membership.objects.filter(organization__in=parliamentary_groups)

    context["vote_without_membership"] = []
    #Pejd cez vse vote in preveri ce obstaja membership za to osebo na ta dan
    with open('zombie_votes.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for ballot in Ballot.objects.all():
            member = ballot.voter.memberships.filter(Q(start_time__lte=ballot.vote.start_time)|Q(start_time=None), Q(end_time__gte=ballot.vote.start_time)|Q(end_time=None), organization__in=parliamentary_groups)
            if not member:
                csvwriter.writerow([ballot.vote.start_time, ballot.voter.id, ballot.voter.name.encode("utf-8")])


def getPersonWithoutVotes():
    # prepare data
    context = {}
    start_time = datetime(day=1, month=8, year=2014)
    end_time = datetime.now()
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))

    data = []

    members = Membership.objects.filter(organization__in=parliamentary_groups)

    with open('poor_voters.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for vote in Vote.objects.all():
            real_voters = vote.ballot_set.all().values_list("voter__id", flat=True)
            fi_voters_memberships = members.filter(Q(start_time__lte=vote.start_time)|Q(start_time=None), Q(end_time__gte=vote.start_time)|Q(end_time=None))
            fi_voters = fi_voters_memberships.values_list("person__id", flat=True)

            personWithoutVotes = list(set(fi_voters)-set(real_voters))

            mems = fi_voters_memberships.filter(person__id__in=personWithoutVotes)
            for personMem in mems:
                csvwriter.writerow([vote.start_time, personMem.id, personMem.person.id, personMem.person.name])

def parserChecker(request):
    context = {}
    context["empty_session"] = []
    context["sessions_for_delete"] = []
    sessions = Session.objects.all().order_by("start_time")
    for session in sessions:
        if not session.vote_set.all() and not session.speech_set.all():
            context["empty_session"].append(session)
    set_of_names = set([ses.name for ses in context["empty_session"]])

    for name in set_of_names:
        sess = Session.objects.filter(name=name)

        context["sessions_for_delete"].append([{"session": ses, "org": ses.organization, "motions": len(ses.motion_set.all()), "votes": len(ses.vote_set.all()), "ballots": sum([len(vote.ballot_set.all()) for vote in ses.vote_set.all()]), "speeches": len(ses.speech_set.all())} for ses in sess])


    return render(request, "debug_parser.html", context)


def postMembersFixer(request):
    context = {}
    context["posts"] = []
    for member in Membership.objects.all():
        posts = member.memberships.all().order_by("start_time")
        start_time = member.start_time
        firstpost = member.memberships.filter(start_time=start_time)
        line = {"member": member, "fails": []}
        if not posts:
            #Post(start_time=member.start_time, end_time=member.end_time, membership=member, role="član", label="cl", organization=member.organization).save()
            #print "Dodajanje novega psota", member
            line["fails"].append({"type": "empty"})
        elif firstpost:
            posts = posts.exclude(start_time=None)
            if posts.count()==0:
                if firstpost[0].end_time != member.end_time:
                    line["fails"].append({"type": "fail", "note": "sam post z None start_timeom je in endtime se ne matcha z membershipom", "posts": posts})
                continue
            #There is a post which start on membership start time
            if posts[0] == firstpost:
                temp_start = posts[0].start_time
                temp_end = posts[0].end_time
                for post in list(posts)[1:]:
                    if post.start_time > temp_end+timedelta(days=2):
                        #print "Lukna"
                        line["fails"].append({"type": "fail", "note": "Med posti je luknja", "posts": posts})
                if list(posts)[-1].end_time != membership.end_time:
                    #print "konc zadnega posta in membership_end nista ista"
                    line["fails"].append({"type": "fail", "note": "endtime ni ok", "posts": posts})
        else:
            line["fails"].append({"type": "fail", "note": "start_time je neki cudn", "posts": posts})
            #print member.person.name, "start membership:", member.start_time, "start post_prvi:", posts[0].start_time, "start post_zadn:", list(posts)[-1].start_time
        context["posts"].append(line)

    print context["posts"]

    return render(request, "post.html", context)


def checkSessions(request, date_=None):
    
    allSessoins = requests.get("https://data.parlameter.si/v1/getSessions/"+date_).json()
    ses = []
    mot = []
    for s in Organization.objects.all():
        session = requests.get("https://data.parlameter.si/v1/getSessionsOfOrg/"+str(s.id)+"/"+date_).json()
        for m in session:
            motionOfSession = requests.get("https://data.parlameter.si/v1/motionOfSession/"+str(m['id'])).json()
            mot.append({"Ime seje":m['name'], "St. glasovanj":len(motionOfSession)})
        ses.append({"Ime organizacije":s.name, "St. sej":len(session), "Seje":mot})
        mot = []
    out = {
    "DZ":{"Število sej": len(allSessoins), "Po org":ses}

    }
    return JsonResponse(out)

def membersFlowInOrg(request):
    context = {}
    context["orgs"]=[]
    orgs_all = requests.get("https://data.parlameter.si/v1/getOrganizatonByClassification").json()
    orgs = [ org["id"] for org in orgs_all["working_bodies"] + orgs_all["council"] ]
    for org in orgs:
        flow = []
        org_id = org
        print org
        pgRanges = requests.get("https://data.parlameter.si/v1/getMembersOfOrgsRanges/"+str(org_id)+"/"+datetime.now().strftime("%d.%m.%Y")).json()
        for pgRange in pgRanges:
            count = len([member for pg in pgRange["members"].values() for member in pg])
            members_ids = [member for pg in pgRange["members"].values() for member in pg]
            flow.append({"count": {"count": count, "start_date": pgRange["start_date"], "end_date": pgRange["end_date"]}, "members": [member for pg in pgRange["members"].values() for member in pg]})
            if len(flow)>1:
                flow[-1]["added"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else ""} for x in flow[-1]["members"] if x not in flow[-2]["members"]]
                flow[-1]["removed"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, end_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, end_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M")) else None} for x in flow[-2]["members"] if x not in flow[-1]["members"]]
                context["allMps"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else x} for x in flow[-1]["members"]]
            else:
                flow[-1]["added"] = [{"name": Person.objects.get(id=x).name, "person_id": x} for x in flow[-1]["members"]]
        try:
            context["orgs"].append({"name":Organization.objects.get(id=org_id).name, "flow":flow, "allMps": context["allMps"]})
        except:
            context["orgs"].append({"name": "ID: "+str(org_id), "flow":flow,  "allMps": context["allMps"], "allMps": context["allMps"]})
    return render(request, "org_memberships.html", context)


def membersFlowInPGs(request):
    context = {}
    context["orgs"]=[]
    orgs_all = requests.get("https://data.parlameter.si/v1/getOrganizatonByClassification").json()
    orgs = [ org["id"] for org in orgs_all["parliamentary_groups"]]
    for org in orgs:
        flow = []
        org_id = org
        print org
        pgRanges = requests.get("https://data.parlameter.si/v1/getMembersOfOrgsRanges/"+str(org_id)+"/"+datetime.now().strftime("%d.%m.%Y")).json()
        for pgRange in pgRanges:
            count = len([member for pg in pgRange["members"].values() for member in pg])
            members_ids = [member for pg in pgRange["members"].values() for member in pg]
            flow.append({"count": {"count": count, "start_date": pgRange["start_date"], "end_date": pgRange["end_date"]}, "members": [member for pg in pgRange["members"].values() for member in pg]})
            if len(flow)>1:
                flow[-1]["added"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else ""} for x in flow[-1]["members"] if x not in flow[-2]["members"]]
                flow[-1]["removed"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, end_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, end_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M")) else None} for x in flow[-2]["members"] if x not in flow[-1]["members"]]
                context["allMps"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__id=org_id, person__id=x, start_time=(datetime.strptime(flow[-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else x} for x in flow[-1]["members"]]
            else:
                flow[-1]["added"] = [{"name": Person.objects.get(id=x).name, "person_id": x} for x in flow[-1]["members"]]
        try:
            context["orgs"].append({"name":Organization.objects.get(id=org_id).name, "flow":flow, "allMps": context["allMps"]})
        except:
            context["orgs"].append({"name": "ID: "+str(org_id), "flow":flow, "allMps": context["allMps"]})
    return render(request, "org_memberships.html", context)

def membersFlowInDZ(request):
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))

    context = {}
    context["orgs"]=[]
    context["count_of_persons"] = []
    pgRanges = requests.get("https://data.parlameter.si/v1/getMembersOfPGsRanges/"+datetime.now().strftime("%d.%m.%Y")).json()
    for pgRange in pgRanges:
        count = len([member for pg in pgRange["members"].values() for member in pg])
        members_ids = [member for pg in pgRange["members"].values() for member in pg]
        context["count_of_persons"].append({"count": {"count": count, "start_date": pgRange["start_date"], "end_date": pgRange["end_date"]}, "members": [member for pg in pgRange["members"].values() for member in pg]})
        if len(context["count_of_persons"])>1:
            context["count_of_persons"][-1]["added"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else ""} for x in context["count_of_persons"][-1]["members"] if x not in context["count_of_persons"][-2]["members"]]
            context["count_of_persons"][-1]["removed"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, end_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, end_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")-timedelta(days=1)).strftime("%Y-%m-%d %H:%M")) else None} for x in context["count_of_persons"][-2]["members"] if x not in context["count_of_persons"][-1]["members"]]
            context["allMps"] = [{"name": Person.objects.get(id=x).name, "membership": Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M"))[0] if Membership.objects.filter(organization__in=parliamentary_groups, person__id=x, start_time=(datetime.strptime(context["count_of_persons"][-1]["count"]["start_date"], "%d.%m.%Y")).strftime("%Y-%m-%d %H:%M")) else x} for x in context["count_of_persons"][-1]["members"]]
        else:
            context["count_of_persons"][-1]["added"] = [{"name": Person.objects.get(id=x).name, "person_id": x} for x in context["count_of_persons"][-1]["members"]]
    context["orgs"].append({"name": "DZ:", "flow":context["count_of_persons"],  "allMps": context["allMps"]})
    return render(request, "org_memberships.html", context)

def getMPsOrganizationsByClassification():
    classes = ["skupina prijateljstva", "delegacija", "komisija", "poslanska skupina", "odbor", "kolegij", "preiskovalna komisija", "", "nepovezani poslanec"]
    with open('members_orgs.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Person"]+[clas for clas in classes])
        parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
        pgs = Membership.objects.filter(organization__in=parliamentary_group)
        for person_mps in pgs:
            memberships = person_mps.person.memberships.all()
            counter = {"skupina prijateljstva":[], "delegacija": [], "komisija" : [], "poslanska skupina": [], "odbor": [], "kolegij": [], "preiskovalna komisija": [], "": [], "nepovezani poslanec":[]}
            for mem in memberships:
                counter[mem.organization.classification].append(smart_str(mem.organization.name))
            csvwriter.writerow([smart_str(person_mps.person.name)]+[",".join(counter[clas]) for clas in classes])

def updateSpeechOrg ():
    for speech in Speech.objects.all():
        members =  requests.get('https://data.parlameter.si/v1/getMembersOfPGsOnDate/'+speech.start_time.strftime('%d.%m.%Y')).json()
        for ids, mem in members.items():
            if speech.speaker.id in mem:
                print Organization.objects.get(id=int(ids)).name
                print speech.id
                speech.party=Organization.objects.get(id=int(ids))
                speech.save()
                print "org: ",ids

def getNonPGSpeekers():
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") | Q(classification="nepovezani poslanec"))
    memberships = Membership.objects.filter(organization=parliamentary_group).values_list("person__id", flat=True)
    ids=list(memberships)
    Speech.objects.all().exclude(speaker__id__in=ids)
    nonPgSpeakers = Speech.objects.all().exclude(speaker__id__in=ids).values_list("speaker__id", flat=True)
    nonPGspeekers = {speaker : {"name": Person.objects.get(id=speaker).name, "id": Person.objects.get(id=speaker).id, "count": Speech.objects.filter(speaker__id=speaker).count()} for speaker in nonPgSpeakers}
    data = sorted(nonPGspeekers.values(), key=lambda k,: k["count"], reverse=True)
    with open('non_pg_speakers.csv', 'w') as csvfile:
        svwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for person in data:
            csvwriter.writerow([person["id"], smart_str(person["name"]), person["count"]])

def updateMotins():
    for motion in Motion.objects.all():
        yes = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("za", 0)
        against = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("proti", 0)
        kvorum = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("kvorum", 0)
        no = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("ni", 0)
        if motion.text == "Dnevni red v celoti" or motion.text == "Širitev dnevnega reda".decode('utf8'):
            if yes > (yes + against + kvorum + no) / 2:
                print 1
                motion.result = 1
                motion.save()
            else:
                print 0
                motion.result = 0
                motion.save()

def exportTagsOfVotes():
    with open('tagged_votes.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, 
                               delimiter=',',
                               quotechar='|', 
                               quoting=csv.QUOTE_MINIMAL)
        votes = Vote.objects.all() 
        for vote in votes:
            if vote.tags.all():
                print vote.session.name, vote.motion.text, vote.tags.all().values_list("name", flat=True)
                csvwriter.writerow([unicode(vote.session.name), unicode(vote.motion.text), unicode(";".join(vote.tags.all().values_list("name", flat=True)))])
    return 1


def exportResultOfVotes():
    with open('result_of_votes.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, 
                               delimiter=',',
                               quotechar='|', 
                               quoting=csv.QUOTE_MINIMAL)
        votes = Motion.objects.all()
        count = 0 
        for vote in votes:
            csvwriter.writerow([unicode(vote.session.name), unicode(vote.text), unicode(vote.result)])
            if vote.result:
                count += 1
        print count
    return 1
