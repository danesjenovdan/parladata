# -*- coding: utf-8 -*-
from parladata.models import *
from django.db.models import Q
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from collections import Counter
import csv
from django.utils.encoding import smart_str
from django.db.models import Count
import re
from django.core.mail import send_mail

DZ_ID = 95
PS_NP = ['poslanska skupina', 'nepovezani poslanec']
PS = 'poslanska skupina'


def AverageList(list):
    """Returns average from list of integers."""

    return sum(list) / float(len(list))


def AverageListOfDic(list, key):
    """Returns average from dictionary of integers."""

    data = [i[key] for i in list]
    return sum(data) / float(len(list))


def MaxListOfDic(list, key):
    """Returns maximum of list of dictionaries."""

    data = [i[key] for i in list]
    return max(data)


def getMPObjects(date_=None):
    """Return objects of all parlament members.
       MP = Members of parlament
       Function: git config
    """

    if not date_:
        date_ = datetime.now()
    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                      Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    members = members.filter(Q(start_time__lte=date_) |
                             Q(start_time=None),
                             Q(end_time__gte=date_) |
                             Q(end_time=None))
    return [i.person for i in members]


def getCurrentMandate():
    """Returns current mandate."""

    return Mandate.objects.all()[-1]


def getVotesDict(date=None):
    """Returns all voters in a dictionary."""

    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                      Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    votes = dict()
    for m in list(set(members.values_list("person", flat=True))):
        if date:
            date2 = datetime.strptime(date, settings.API_DATE_FORMAT) + timedelta(days=1) - timedelta(seconds=1)
            ballots = list(Ballot.objects.filter(voter__id=m,
                                                 vote__start_time__lte=date2).order_by('vote__start_time').values_list('option', 'vote_id'))
        else:
            ballots = list(Ballot.objects.filter(voter__id=m).order_by('vote__start_time').values_list('option', 'vote_id'))

        if ballots:
            votes[str(m)] = {ballot[1]: ballot[0] for ballot in ballots}
        # Work around if ther is no ballots for member
        else:
            votes[str(m)] = {}
    return votes


def voteToLogical(vote):
    """Returns 1 instead of 'za' and 0 of 'proti'."""

    if vote == "za":
        return 1
    elif vote == "proti":
        return 0
    else:
        return -1


def getFails():
    """Function for finding MPs membersihp date issues."""

    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                      Q(classification="nepovezani poslanec"))
    members = Membership.objects.filter(organization__in=parliamentary_group)
    members = members.filter()
    start = Vote.objects.all().order_by("start_time")[0].start_time
    out = {}
    for member in members:
        if member.start_time is None and member.end_time is None:
            votes = Vote.objects.filter(Q(start_time__gte=start) |
                                        Q(end_time__lte=datetime.now()))
        elif member.start_time is None and member.end_time is not None:
            votes = Vote.objects.filter(Q(start_time__gte=start) |
                                        Q(end_time__lte=member.end_time))
        elif member.start_time is not None and member.end_time is not None:
            votes = Vote.objects.filter(Q(start_time__gte=member.start_time) |
                                        Q(end_time__lte=member.end_time))
        elif member.start_time is not None and member.end_time is None:
            votes = Vote.objects.filter(Q(start_time__gte=member.start_time) |
                                        Q(end_time__lte=datetime.now()))
        for vote in votes:
            if not Ballot.objects.filter(voter=member.person, vote=vote):
                if member.person.id in out.keys():
                    out[member.person.id].append(vote.start_time)
                else:
                    out[member.person.id] = [vote.start_time]
    print out


def getMembershipDuplications(request):
    """
    Debug method:
        - check if person has membership in more than one party at time
        - check if person has more than one membership per organization
        - organization role chacher
        - chack members in DZ
        - members without votres
        - check if person has more than one post per organization
    """

    context = {}
    start_time = datetime(day=1, month=8, year=2014)
    end_time = datetime.now()
    parliamentary_groups = Organization.objects.filter(classification__in=PS_NP)

    members = Membership.objects.filter(organization__in=parliamentary_groups)

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
                # preverji da je chk_mem pred membershipom
                if chk_end >= mem_start:
                    # FAIL
                    out.append({"member": membership.person,
                                "mem1": membership,
                                "mem2": chk_mem})

            elif chk_start >= mem_start:
                # preverji da je chk_mem pred membershipom
                if mem_end >= chk_start:
                    # FAIL
                    out.append({"member": membership.person,
                                "mem1": membership,
                                "mem2": chk_mem})

            else:
                print "WTF enaka sta?"

    context["data"] = out

    # check if one person have more then one membership per organization
    members_list = list(members.values_list("person", flat=True))
    org_per_person = []
    added_mems = []
    for member in members_list:
        temp = dict(Counter(list(members.filter(person__id=member).values_list("organization", flat=True))))
        print temp
        for key, val in temp.items():
            if val > 1 and not Membership.objects.filter(person__id=member,
                                                         organization__id=key)[0].id in added_mems:
                print val
                added_mems.append(Membership.objects.filter(person__id=member,
                                                            organization__id=key)[0].id)
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
    """Checks if memberships of PGs are ok."""

    context = {}
    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                       Q(classification="nepovezani poslanec"))
    context["vote_without_membership"] = []
    with open('zombie_votes.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for ballot in Ballot.objects.all():
            member = ballot.voter.memberships.filter(Q(start_time__lte=ballot.vote.start_time) |
                                                     Q(start_time=None),
                                                     Q(end_time__gte=ballot.vote.start_time) |
                                                     Q(end_time=None), organization__in=parliamentary_groups)
            if not member:
                csvwriter.writerow([ballot.vote.start_time,
                                    ballot.voter.id,
                                    ballot.voter.name.encode("utf-8")])


def getPersonWithoutVotes():
    """Returns all MPs without votes."""

    parliamentary_groups = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                       Q(classification="nepovezani poslanec"))

    members = Membership.objects.filter(organization__in=parliamentary_groups)

    with open('poor_voters.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|',
                                        quoting=csv.QUOTE_MINIMAL)
        for vote in Vote.objects.all():
            real_voters = vote.ballot_set.all().values_list("voter__id", flat=True)
            fi_voters_memberships = members.filter(Q(start_time__lte=vote.start_time) |
                                                   Q(start_time=None),
                                                   Q(end_time__gte=vote.start_time) |
                                                   Q(end_time=None))
            fi_voters = fi_voters_memberships.values_list("person__id", flat=True)

            personWithoutVotes = list(set(fi_voters) - set(real_voters))

            mems = fi_voters_memberships.filter(person__id__in=personWithoutVotes)
            for personMem in mems:
                csvwriter.writerow([vote.start_time,
                                    personMem.id,
                                    personMem.person.id,
                                    personMem.person.name])


def postMembersFixer(request):
    """Fixes post of PGs."""

    context = {}
    context["posts"] = []
    for member in Membership.objects.all():
        posts = member.memberships.all().order_by("start_time")
        start_time = member.start_time
        firstpost = member.memberships.filter(start_time=start_time)
        line = {"member": member, "fails": []}
        if not posts:
            line["fails"].append({"type": "empty"})
        elif firstpost:
            posts = posts.exclude(start_time=None)
            if posts.count() == 0:
                if firstpost[0].end_time != member.end_time:
                    line["fails"].append({"type": "fail",
                                          "note": "sam post z None start_timeom je in endtime se ne matcha z membershipom",
                                          "posts": posts})
                continue
            # There is a post which start on membership start time
            if posts[0] == firstpost:
                temp_end = posts[0].end_time
                for post in list(posts)[1:]:
                    if post.start_time > temp_end + timedelta(days=2):
                        line["fails"].append({"type": "fail",
                                              "note": "Med posti je luknja",
                                              "posts": posts})
                if list(posts)[-1].end_time != membership.end_time:
                    line["fails"].append({"type": "fail",
                                          "note": "endtime ni ok",
                                         "posts": posts})
        else:
            line["fails"].append({"type": "fail",
                                  "note": "start_time je neki cudn",
                                  "posts": posts})
        context["posts"].append(line)

    return render(request, "post.html", context)


def checkSessions(request, date_=None):
    """Returns number of sessions adjust to organization."""

    allSessoins = requests.get("https://data.parlameter.si/v1/getSessions/" + date_).json()
    ses = []
    mot = []
    for s in Organization.objects.all():
        session = requests.get("https://data.parlameter.si/v1/getSessionsOfOrg/" + str(s.id) + "/" + date_).json()
        for m in session:
            motionOfSession = requests.get("https://data.parlameter.si/v1/motionOfSession/" + str(m['id'])).json()
            mot.append({"Ime seje": m['name'], "St. glasovanj": len(motionOfSession)})
        ses.append({"Ime organizacije": s.name, "St. sej": len(session), "Seje": mot})
        mot = []
    out = {"DZ": {"Število sej": len(allSessoins), "Po org": ses}}
    return JsonResponse(out)


def membersFlowInOrg(request):
    """
    Debug method which shows when members joins and leave oragnizations.
    """
    context = {}
    context["orgs"]=[]
    orgs_all = requests.get("https://data.parlameter.si/v1/getOrganizatonByClassification").json()
    orgs = [ org["id"] for org in orgs_all["working_bodies"] + orgs_all["council"]]
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
    """
    Debug method which shows when members joins and leave partys.
    """
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
    """
    Debug method which shows when members joins and leave DZ.
    """
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
    """
    CSV export memberships of all DZ members grouped by classification
    """
    classes = ["skupina prijateljstva",
               "delegacija",
               "komisija",
               "poslanska skupina",
               "odbor", "kolegij",
               "preiskovalna komisija",
               "",
               "nepovezani poslanec"]
    with open('members_orgs.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=';',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Person"]+[clas for clas in classes])
        parliamentary_group = Organization.objects.filter(classification__in=PS_NP)
        pgs = Membership.objects.filter(organization__in=parliamentary_group)
        for person_mps in pgs:
            memberships = person_mps.person.memberships.all()
            counter = {"skupina prijateljstva": [],
                       "delegacija": [],
                       "komisija": [],
                       "poslanska skupina": [],
                       "odbor": [],
                       "kolegij": [],
                       "preiskovalna komisija": [],
                       "": [],
                       "nepovezani poslanec": []}
            for mem in memberships:
                c_obj = counter[mem.organization.classification]
                c_obj.append(smart_str(mem.organization.name))
            data = [smart_str(person_mps.person.name)]
            data = data + [",".join(counter[clas]) for clas in classes]
            csvwriter.writerow(data)

def updateSpeechOrg():
    """Updates all speeches."""

    members =  requests.get('https://data.parlameter.si/v1/getMembersOfPGsRanges').json()
    for mem in members:
        edate = datetime.strptime(mem['end_date'], settings.API_DATE_FORMAT)
        sdate = datetime.strptime(mem['start_date'], settings.API_DATE_FORMAT)
        speeches = Speech.objects.filter(start_time__range=[sdate, edate + timedelta(hours=23, minutes=59)])
        print "count range speeches", speeches.count()
        for spee in speeches:
            for m, ids in mem['members'].items():
                if spee.speaker.id in ids:
                    spee.party = Organization.objects.get(id=int(m))
                    spee.save()


def getNonPGSpeekers():
    """Return speakers that are not in PG."""

    parliamentary_group = Organization.objects.filter(Q(classification="poslanska skupina") |
                                                      Q(classification="nepovezani poslanec"))
    memberships = Membership.objects.filter(organization=parliamentary_group).values_list("person__id", flat=True)
    ids = list(memberships)
    Speech.objects.all().exclude(speaker__id__in=ids)
    nonPgSpeakers = Speech.objects.all().exclude(speaker__id__in=ids).values_list("speaker__id", flat=True)
    nonPGspeekers = {speaker: {"name": Person.objects.get(id=speaker).name,
                                "id": Person.objects.get(id=speaker).id,
                                "count": Speech.objects.filter(speaker__id=speaker).count()} for speaker in nonPgSpeakers}
    data = sorted(nonPGspeekers.values(), key=lambda k: k["count"], reverse=True)
    with open('non_pg_speakers.csv', 'w') as csvfile:
        svwriter = csv.writer(csvfile, delimiter=',',quotechar='|',
                                       quoting=csv.QUOTE_MINIMAL)
        for person in data:
            csvwriter.writerow([person["id"], smart_str(person["name"]), person["count"]])


def updateMotins():
    """Updates motion."""

    for motion in Motion.objects.all():
        yes = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("za", 0)
        against = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("proti", 0)
        kvorum = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("kvorum", 0)
        no = dict(Counter(Ballot.objects.filter(vote__motion=motion).values_list("option", flat=True))).get("ni", 0)
        if motion.text == "Dnevni red v celoti" or motion.text == "Širitev dnevnega reda".decode('utf8'):
            if yes > (yes + against + kvorum + no) / 2:
                motion.result = 1
                motion.save()
            else:
                motion.result = 0
                motion.save()


def exportTagsOfVotes():
    """Exports all tags of all votes."""

    with open('tagged_votes.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        votes = Vote.objects.all()
        for vote in votes:
            if vote.tags.all():
                print vote.session.name, vote.motion.text, vote.tags.all().values_list("name", flat=True)
                csvwriter.writerow([unicode(vote.session.name),
                                    unicode(vote.motion.text),
                                    unicode(";".join(vote.tags.all().values_list("name", flat=True)))])
    return 1


def exportResultOfVotes():
    """Exports results of votes."""

    with open('result_of_votes.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        votes = Motion.objects.all()
        count = 0
        for vote in votes:
            csvwriter.writerow([unicode(vote.session.name),
                                unicode(vote.text),
                                unicode(vote.result)])
            if vote.result:
                count += 1
    return 1


def updateBallotOrg():
    """Updates all ballots."""

    for ballot in Ballot.objects.all():
        members = requests.get('https://data.parlameter.si/v1/getMembersOfPGsOnDate/' + ballot.vote.session.start_time.strftime('%d.%m.%Y')).json()
        for ids, mem in members.items():
            if ballot.voter.id in mem:
                print Organization.objects.get(id=int(ids)).name
                print ballot.id
                ballot.voterparty = Organization.objects.get(id=int(ids))
                ballot.save()
                print "org: ", ids


def migrateVotesInMotions():
    """Migrates objects Votes to Motion."""

    for vote in Motion.objects.filter(created_at__gte=datetime.now() - timedelta(minutes=60)):
        org = vote.session.organization
        session_name = vote.session.name
        ses = Session.objects.filter(name=session_name,
                                     created_at__lte=datetime.now() - timedelta(minutes=60),
                                     organization=org)
        vote.session = ses[0]
        vote.save()
        print ses[0].name, ses[0].created_at, vote.created_at


def showSpeechesDuplicate():
    """Return all deplicated speeches."""

    def showData(qverySet, f):
        if len(list(set(list(qverySet.values_list("session_id", flat=True))))) > 1:
            f.write(qverySet[0].content)
            f.write(qverySet[0].speaker.name)
            f.write(qverySet[0].session.organization.name)

            f.write("imajo isti cas" if len(list(set(list(qverySet.values_list("start_time", flat=True))))) < 2 else "razlicen cas")
            f.write(str(len(list(set(list(qverySet.values_list("start_time", flat=True)))))) + " " + str(len(qverySet.values_list("start_time", flat=True))))
            f.write(str(list(qverySet.values_list("session_id"))))
            f.write(str(list(qverySet.values_list("session__name"))))
            f.write(str(list(qverySet.values_list("session__organization__name"))))
            f.write("")

    ds = Speech.objects.values('content').annotate(Count('id')).order_by().filter(id__count__gt=1)
    cl = [d["content"] for d in ds]
    f = open('duplicates.txt', 'w')

    for content in cl:
        speeches = Speech.objects.filter(content=content)
        speakers = speeches.values("speaker_id").annotate(Count('id')).order_by().filter(id__count__gt=1)
        for speaker in speakers:
            showData(speeches.filter(speaker_id=speaker["speaker_id"]), f)
    c.close()


def updateSessionInReviewStatus(filename):
    """Updates in review status of sessions."""

    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            for candidate in row:
                id_session = None
                try:
                    id_session = int(candidate)
                except:
                    print "ni id :)", candidate
                if id_session:
                    session = Session.objects.filter(id=id_session)
                    if session.count() == 1:
                        print "updejtam", session[0].name, "ivan"
                        session[0].in_review = True
                        session[0].save()
                    else:
                        print "Neki ni ql s sejo count je : ", session.count()


def determineSession(date_):
    """Returns session of DZ (redna seja) on given date."""

    fdate = datetime.strptime(date_, '%d.%m.%Y')
    toDate = fdate + timedelta(hours=23, minutes=59)
    session = Session.objects.filter(start_time__gte=fdate,
                                     start_time__lte=toDate,
                                     organization__id=95,
                                     name__icontains="redna"
                                     )
    if session:
        return session[0]
    else:
        return None


def determinePerson(full_name):
    """Checks if the person is in the attribute name_parser."""

    person = Person.objects.filter(name_parser__icontains=full_name)
    if person:
        return person[0]
    else:
        return None


def getIdSafe(obj):
    """Returns ID of object if exists."""

    if obj:
        return obj.id
    else:
        None


def replace_all(text, dic):
    """Replace all words in text attribute
       with the words in dic attribute.
    """

    for i, j in dic.iteritems():
        pattern = re.compile(i, re.IGNORECASE)
        text = pattern.sub(j, text)
    return text


def jointSessionDataFix():
    ss = Session.objects.all()
    for s in ss:
        s.organizations.add(s.organization)


def deleteMotionsWithoutText():
    Motion.objects.filter(text="").delete()


def sendMailForEditVotes(votes):
    """
    Send mail to data admin to for tag votes and set votes results
    """
    motionAdmin = 'https://data.parlameter.si/admin/parladata/motion/'
    setMotionsUrl = 'https://analize.parlameter.si/v1/s/setMotionOfSession/'
    tagsUrl = 'https://data.parlameter.si/tags/'
    pageVotes = 'https://parlameter.si/seja/glasovanja/'
    pageGraph = 'https://parlameter.si/seja/glasovanje/'
    reNavigatePage = 'https://parlameter.si/fetch/sps?t=vkSzv8Nu4eDkLBk7kUw4BBhyLjysJm'
    updated_votes = Vote.objects.filter(id__in=votes.keys())
    motionUrls = []
    updateUrls = []
    sesUpdateUrls = []
    graphUpdateUrls = []
    for session in list(set(votes.values())):
        url = setMotionsUrl + str(session)
        updateUrls.append(url)
        url = pageVotes + str(session) + '?forceRender=true'
        sesUpdateUrls.append(url)
    for vote, session in votes.items():
        url = pageGraph + str(session) + '/' + str(vote) + '?forceRender=true'
        graphUpdateUrls.append(url)

    pre = 'Na naslednji povezavi najdes glasovanja, ki jih je potrebno poupdejtat: \n'
    content = pre + "\n " + motionAdmin
    content += '\n \n nato jih potagaj: \n' + tagsUrl
    content += "\n \n Ko vse to uredis poklikaj naslednje linke, da vse to spravis na parlalize: \n"
    content += "\n".join(updateUrls)
    content += "\n Pozen se to: \n"
    content += reNavigatePage
    content += "\n \n Zdj spremembe dodaj na sezname glasovanj od sej: \n"
    content += "\n".join(sesUpdateUrls)
    content += "\n \n Pa se grafe glasovanj: \n"
    content += "\n".join(graphUpdateUrls)
    content += "\n \n Lep dan ti zelim ;)"
    send_mail('Nekaj novih glasovanj je za pottagat :)',
              content,
              'test@parlameter.si',
              [admin[1] for admin in settings.ADMINS + settings.DATA_ADMINS],
              fail_silently=False,)


def parseRecipient(text, date_of):
    mv = Organization.objects.filter(classification__in=['vlada',
                                                         'ministrstvo',
                                                         'sluzba vlade',
                                                         'urad vlade'])
    out = []
    orgs = mv.values('name', 'id')
    data = {org['name'].replace(',', ''): org for org in orgs}
    rts = text.split(', ')
    for rt in rts:
        role = None
        added = False
        text = ''
        if 'minister' in rt:
            text = rt.split('minister ')[1]
            text = text.split(' v funkciji')[0]
        elif 'ministrica' in rt:
            text = rt.split('ministrica ')[1]
            text = text.split(' v funkciji')[0]
        elif 'predsednik Vlade' in rt:
            text = 'Vlada'
            text = text.split(' v funkciji')[0]
            role = ['predsednik', 'predsednica']
        elif 'Vlada' in rt:
            out.append({'recipient': mv.get(name='Vlada'), 'type': 'org'})
            continue
        elif 'generaln' in rt and 'sekretar' in rt and 'Vlade' in rt:
            text = 'Vlada'
            text = text.split(' v funkciji')[0]
            role = ['generalni sekretar', 'generalna sekretarka']

        if text:
            # edge cases or fails on government page
            if 'za razvoj strate\u0161ke projekte in kohezijo' in text:
                text = 'vlade za razvoj in evropsko kohezijsko politiko'
            elif 'za Slovence v zamejstvu in po svetu' in text:
                text = 'Urad vlade za Slovence v zamejstvu in po svetu'
            elif 'infrastrukturo in prostor' in text:
                text = 'za infrastrukturo'
            for d in data:
                if text in d:
                    org = mv.get(id=data[d]['id'])
                    posts = org.posts.filter(Q(start_time__lte=date_of) |
                                             Q(start_time=None),
                                             Q(end_time__gte=date_of) |
                                             Q(end_time=None))
                    if role:
                        posts = posts.filter(role__in=role)
                    if posts:
                        out.append({'recipient': posts[0].membership.person,
                                    'type': 'person'})
                        added = True
                    else:
                        print 'There is no POsts', text, date_of
                    break
                else:
                    pass

        if not added:
            out.append(None)
    return out
