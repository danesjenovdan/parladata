from django.db.models import Count

from parladata.models import Speech, Question, Vote, Membership, Organization, Ballot, Person, Area, Post
from parladata.utils import parseRecipient
from django.db.models import Q
from django.conf import settings

from datetime import datetime
from collections import *

import requests
from requests.auth import HTTPBasicAuth

import csv
import importlib

PS_NP = ['poslanska skupina', 'nepovezani poslanec']


def fixSpeeches():
    s = Speech.getValidSpeeches(datetime(2017, 2, 6, 0, 0)).filter(speaker__id=53)
    dups = (s.values('order', 'session_id', 'start_time')
            .annotate(count=Count('id'))
            .values('order', 'session_id', 'start_time')
            .order_by()
            .filter(count__gt=1)
            )
    a = 0
    for d in dups:
        multi = s.filter(start_time=d["start_time"], order=d["order"], session_id=d["session_id"]).order_by("valid_from")
        # print multi[0].valid_from
        m = multi[0]
        m.valid_to = inf
        m.save()
        multi = multi.exclude(id=m.id)
        # print multi.values_list("valid_from", flat=True)
        multi.delete()

    for i in range(45):
        print(Speech.getValidSpeeches(new_year+timedelta(i)).filter(speaker__id=41).count())


def setRecipientsToQuestions():
    questions = Question.objects.all()
    not_a_member = []
    for question in questions:
        text = question.recipient_text
        date = question.date
        recipients = parseRecipient(text, date)
        print(recipients, text)
        for i, recipient in enumerate(recipients):
            if recipient:
                if recipient['type'] == 'person':
                    print('save person')
                    question.recipient_person.add(recipient['recipient'])
                elif recipient['type'] == 'org':
                    print('save org')
                    question.recipient_organization.add(recipient['recipient'])
                elif recipient['type'] == 'post':
                    print('save post')
                    question.recipient_post.add(recipient['recipient'])
            else:
                #not_a_member.append({text.split(',')[i]: date})
                pass
    return not_a_member


def fixBallotsVoterParty(person_id):
    """
    set voter party for each ballot of person
    """
    #mems = Membership.objects.filter(person_id=person_id,
    #                                 organization__classification__in=PS_NP)

    mems = Membership.objects.filter(person_id=person_id,
                                     role='voter').exclude(on_behalf_of=None)

    print(mems)
    for mem in mems:
        start_time, end_time = getStartEndTime(mem)
        ballots = Ballot.objects.filter(voter_id=person_id,
                                        vote__start_time__gte=start_time,
                                        vote__start_time__lte=end_time)
        print(list(set(list(ballots.values_list("voterparty", flat=True)))))
        ballots.update(voterparty=mem.on_behalf_of)


def getStartEndTime(membership):
    if membership.start_time:
        start_time = membership.start_time
    else:
        start_time = datetime(day=1, month=8, year=2014)
    if membership.end_time:
        end_time = membership.end_time
    else:
        end_time = datetime.now()
    return start_time, end_time


def fixBallotsVoterPartyByVote(vote_id):
    vote = Vote.objects.get(id=vote_id)
    members = Membership.objects.filter(Q(start_time__lte=vote.start_time) |
                                        Q(start_time=None),
                                        Q(end_time__gte=vote.start_time) |
                                        Q(end_time=None),
                                        organization__classification__in=PS_NP)
    orgs = list(set(list(members.values_list("organization_id", flat=True))))
    for org in orgs:
        people = members.filter(organization_id=org).values_list("person_id",
                                                                 flat=True)
        ballots = Ballot.objects.filter(voter__in=people,
                                        vote=vote)

        org_obj = Organization.objects.get(id=org)
        ballots.update(voterparty=org_obj)


def addAuthorOrgToQuestion():
    true_start_time = datetime(day=1, month=8, year=2014)
    a_ids = list(set(list(Question.objects.all().values_list("author__id", flat=True))))
    for author in a_ids:
        memberships = Membership.objects.filter(organization__classification__in=PS_NP,
                                                person=author)
        for membership in memberships:
            start_time = membership.start_time if membership.start_time else true_start_time
            end_time = membership.end_time if membership.end_time else datetime.now()
            Question.objects.filter(date__gte=start_time,
                                    date__lte=end_time,
                                    author_id=author).update(author_org=membership.organization)


def fixSpeakerParty(person_id):
    """
    set voter party for each ballot of person
    """

    party = Membership.objects.filter(person_id=person_id,
                                      role='voter').exclude(on_behalf_of=None)

    ministry = Membership.objects.filter(person_id=person_id,
                                         organization__classification='ministrstvo',
                                         role__in=['minister', 'ministrica'])
    mems = list(party) + list(ministry)
    mems = sorted(mems, key=lambda x: x.start_time)
    print(mems)
    prev_end = None
    for mem in mems:
        start_time, end_time = getStartEndTime(mem)

        speeches = Speech.objects.filter(speaker_id=person_id,
                                         start_time__gte=start_time,
                                         start_time__lte=end_time)
        speeches.update(party=mem.on_behalf_of)


def uk_motion_result():
    for motion in Motion.objects.all():
        vote = motion.vote.all()[0]
        options = vote.ballot_set.all().values_list("option", flat=True)
        max_opt = Counter(options).most_common(1)[0][0]
        if max_opt == "aye":
            motion.result=1
            motion.save()
        else:
            motion.result=0
            motion.save()


def check_person_parser_data():
    fields = ['date_of_birth', 'preferred_pronoun', 'districts', 'education', 'education_level']
    data = []
    for p in pp:
        missing_data = [i for i in fields if not getattr(p, i)]
        if missing_data:
            data.append({'missing': missing_data, 'person': p.name, 'id': p.id, 'url': 'http://51.15.135.53/data/admin/parladata/person/' + str(p.id) + '/'})
    return data


def getPersonsFromOldParlameter():
    import sys
    importlib.reload(sys)
    sys.setdefaultencoding('utf8')
    count = 0
    url = 'https://data.parlameter.si/v1/persons'
    old_people = getDataFromPagerApiDRF(url)
    for person in Person.objects.all():
        old = get_person_by_parser_name(old_people, person.name_parser)
        if old:
            count += 1
            print('update ', person.name.encode('utf-8'), old['name'].encode('utf-8'))
            person.name = old['name']
            #person.family_name = old['family_name']
            #person.given_name = old['given_name']
            #person.additional_name = old['additional_name']
            #person.honorific_prefix = old['honorific_prefix']
            #person.honorific_suffix = old['honorific_suffix']
            #person.previous_occupation = 'poslanec'
            #person.education = old['education']
            #person.education_level = old['education_level']
            #try:
            #    person.mandates = int(old['mandates']) + 1
            #except:
            #    person.mandates = 1
            #person.email = old['email']
            #person.gender = old['gender']
            #person.birth_date = old['birth_date']
            person.save()
        else:
            print('skipp ', person.name.encode('utf-8'))

    print(count)


def get_person_by_parser_name(old_people, name_parser):
    names = name_parser.split(',')
    for p in old_people:
        for p_name in p['name_parser'].split(','):
            if p_name in names:
                return p

    return None


def getDataFromPagerApiDRF(url):
    print(url)
    data = []
    end = False
    page = 1
    while url:
        response = requests.get(url, auth=HTTPBasicAuth('djnd', 'necakajpomladi')).json()
        data += response['results']
        url = response['next']
    return data


def getDuplicatedPersons():
    visited = []
    for p in Person.objects.all():
        d = Person.objects.filter(name_parser__icontains=p.name).exclude(id__in=visited)
        if d.count() > 1:
            for i in d:
                visited.append(i.id)
            merge_people(d)
            print(d)


def merge_people(q_s):
    base_person = q_s.first()
    others = q_s.exclude(id=base_person.id)
    for other in others:
        other.speech_set.all().update(speaker=base_person)
        other.ballot_set.all().update(voter=base_person)
        other.delete()


def find_non_membershis_votes(others_id):
    out = ['id', 'name', 'first_vote', 'last_vote']
    mps = {i:[] for i in  list(set(list(Ballot.objects.filter(voterparty=344, option__in=["for", "against", "abstain"]).values_list("voter__id", flat=True))))}
    for v in Ballot.objects.filter(voterparty=344, option__in=["for", "against", "abstain"]):
        mps[v.voter.id].append(v.vote.start_time)

    for i, m in list(mps.items()):
        out.append([i, Person.objects.get(id=i).name, min(m), max(m)])

    return out


"""
data = {
    310: [261],
    319: [291, 258],
    322: [315],
    324: [308, 329],
    330: [275],
    333: [282, 341, 326],
    334: [266, 303],
    335: [263, 316],
    337: [300],
    339: [268],
    340: [289],
    343: [295, 274],
}
"""
def move_memberships(source_org, dest_org):
    s_pss = Membership.objects.filter(organization__id=source_org)
    d_pss = Membership.objects.filter(organization__id=dest_org)
    print(('source', s_pss, 'dest_org', d_pss))

    dest_org_obj = Organization.objects.get(id=dest_org)

    for ps_m in s_pss:
        print(ps_m.person)
        person = ps_m.person
        dest_membership = d_pss.filter(person=person)
        if dest_membership:
            if ps_m.end_time == None:
                # check start time and fix it
                if dest_membership[0].end_time == None:
                    print('Fixing start time', dest_membership[0].start_time, ps_m.start_time)
                    dest_membership = dest_membership[0]
                    dest_membership.start_time = ps_m.start_time
                    dest_membership.save()

                else:
                    print('This shit does not work')
            else:
                # add new membership
                print('copying memberhsip 2')
                ps_m.pk = None
                ps_m.organization = dest_org_obj
                ps_m.save()

        else:
            # add new membership
            print('copying memberhsip 1', ps_m.start_time, ps_m.end_time)
            ps_m.pk = None
            ps_m.organization = dest_org_obj
            ps_m.save()


def add_posts_from_membership():
    for m in Membership.objects.filter(role='president'):
        Post(role='president',
            label='v',
            organization=m.organization,
            membership=m,
            start_time=m.start_time,
            end_time=m.end_time).save()

    for m in Membership.objects.filter(role='deputy'):
        Post(role='deputy',
            label='namv',
            organization=m.organization,
            membership=m,
            start_time=m.start_time,
            end_time=m.end_time).save()


def change_international_classes():

    org_map = {
        'poslanska skupina': 'pg',
        'nepovezani poslanec': 'unaligned MP',
        'odbor': 'committee',
        'komisija': 'comission',
        'preiskovalna komisija': 'investigative comission',
        'skupina prijateljstva': 'friendship group',
        'delegacija': 'delegation',
        'kolegij': 'council',
        'ministrstvo': 'ministry',
        'vlada': 'gov',
        'sluzba vlade': 'gov_service',
        'urad vlade': 'gov_office'
    }

    for old, new in list(org_map.items()):
        orgs = Organization.objects.filter(classification=old)
        orgs.update(classification=new)

    areas = Area.objects.filter(classification='okraj')
    areas.update(classification='district')

    Membership

def importPersonData(file_name):
    with open(file_name) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            print(row)
            p = Person.objects.get(id=row[0])
            p.previous_occupation = row[2]
            p.education = row[3]
            p.education_level = row[4]
            p.number_of_mandates = row[5]
            p.email = row[6]
            p.preferred_pronoun = row[7]
            p.date_of_birth = datetime.strptime(row[8], settings.API_DATE_FORMAT).date()
            p.number_of_voters = row[11]
            p.save()

            for area_str in row[10].split(','):
                area_str = area_str.strip()
                area = Area.objects.filter(name=area_str)
                if area:
                    area = area[0]
                else:
                    area = Area(name=area_str, classification='district')
                    area.save()
                p.district.add(area)

def find_voters_without_membership():
    out = []
    for ballot in Ballot.objects.all().distinct("voter"):
        voter_ballots = Ballot.objects.filter(voter=ballot.voter)
        memberships = ballot.voter.memberships.filter(role='voter')
        for membership in memberships:
            start_time = membership.start_time if membership.start_time else datetime.min
            end_time = membership.end_time if membership.end_time else datetime.max
            voter_ballots = voter_ballots.exclude(vote__start_time__range=[start_time, end_time])
        if voter_ballots:
            start_times = voter_ballots.values_list('vote__start_time', flat=True)
            out.append({
                'voter': membership.person.name,
                'votes_count': voter_ballots.count(),
                'votes_min_start_time': min(start_times),
                'votes_max_start_time': max(start_times),
                'votes_options': list(voter_ballots.order_by('vote__start_time').values_list('option', flat=True)),
                'queryset': voter_ballots
            })

    return out


def add_absent_ballot_if_membership_exists():
    for ballot in Ballot.objects.all().distinct("voter"):
        print(ballot.voter.name)
        mms = Membership.objects.filter(person=ballot.voter, role="voter")
        voter_ballots = Ballot.objects.filter(voter=ballot.voter)
        votes_on = voter_ballots.values_list("vote_id")
        for m in mms.order_by("start_time"):
            if m.end_time:
                votes = Vote.objects.filter(Q(start_time__gte=m.start_time), Q(start_time__lte=m.end_time), organization_id=199)
            else:
                votes = Vote.objects.filter(Q(start_time__gte=m.start_time), organization_id=199)
            votes_without_ballots = votes.exclude(id__in=votes_on)
            votes_without_ballots = votes_without_ballots.exclude(counter__isnull=False)
            print((votes_without_ballots.count()))
            # add ballots for this votes
            for vote in votes_without_ballots:
                Ballot(vote=vote, voter=ballot.voter, voterparty=m.on_behalf_of, option='absent').save()


def unknown_sniperts():
    da = AgendaItem.objects.values('name')\
                .annotate(Count('id'), 'id') \
                .order_by()\
                .filter(id__count__gt=1)

    now=datetime.now()
    for d in da:
        ais = AgendaItem.objects.filter(name=d['name']).order_by("created_at")
        s1 = ais[0].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now)
        s2 = ais[1].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now)
        c1 = s1.count()
        c2 = s2.count()
        if c1 != 0 and c2 != 0:
            #print(ais[0].created_at, ais[1].created_at)
            print(c1, c2)
            sc1 = list(s1.values_list("content", flat=True))
            sc2 = list(s2.values_list("content", flat=True))
            inter = intersect(sc1, sc2)
            inter_c=len(inter)
            if c1>c2:
                print('wird')
            print(inter_c)
            if inter_c == c1:
                print(ais[0].session.name)
            cc+=1
            #print inter
            if c2 < 10:
                print list(s1.values_list('content'))
                print list(s2.values_list('content'))
            print


    cc=0
    sessions=[]
    for d in da:
        ais = AgendaItem.objects.filter(name=d['name']).order_by("created_at")
        s1 = ais[0].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now).order_by('order')
        s2 = ais[1].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now).order_by('order')
        c1 = s1.count()
        c2 = s2.count()
        if c1 != 0 and c2 != 0:
            #print(ais[0].created_at, ais[1].created_at)
            print(c1, c2)
            sc1 = list(s1.values_list("content", flat=True))
            sc2 = list(s2.values_list("content", flat=True))
            inter = intersect(sc1, sc2)
            inter_c=len(inter)
            if c1>c2:
                print('wird')
                print(s1[0].agenda_items.all().values_list('name', flat=True))
                print(s2[0].agenda_items.all().values_list('name', flat=True))
            print(inter_c)
            print(ais[0].session.id)
            if inter_c == c1:
            cc+=1
            sessions.append(ais[0].session.id)
            valid_to = s2[0].created_at
            print('UPDATE')
            for s in s1:
                s.valid_to=valid_to
                s.save()
            print 'UPDATED', s1.count()
            if s1[0].content==s2[0].content and s1[2].content==s2[2].content:
                print list(s1[:5].values_list('content'))
                print list(s2[:5].values_list('content'))
                cc+=1
                sessions.append(ais[0].session.id)
                print('UPDATE')
                for s in s1:
                    s.valid_to=valid_to
                    s.save()
                print 'UPDATED', s1.count()
            print


    for i in ids:
        s1 = Speech.objects.get(id=i[0])
        a1=s1.agenda_items.all()
        s2 = Speech.objects.get(id=i[1])
        a2=s2.agenda_items.all()
        if s1.valid_to == s2.valid_to and s1.order == s2.order:
            print a1
            print a2
            print s1.content
            print s1.order, s2.order
            print s1.id
            print
            if a1[0].created_at > a2[0].created_at:
                a = a1[0]
                ao = a2[0]
            else:
                a = a2[0]
                ao = a1[0]

            ais = [a, ao]
            s1 = ais[0].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now).order_by('order')
            s2 = ais[1].speeches_many.all().filter(valid_from__lt=now, valid_to__gt=now).order_by('order')
            c1 = s1.count()
            c2 = s2.count()
            if c1 != 0 and c2 != 0:
                #print(ais[0].created_at, ais[1].created_at)
                print(c1, c2)
                sc1 = list(s1.values_list("content", flat=True))
                sc2 = list(s2.values_list("content", flat=True))
                inter = intersect(sc1, sc2)
                inter_c=len(inter)
                if c1>c2:
                    print('wird')
                    print(s1[0].agenda_items.all().values_list('name', flat=True))
                    print(s2[0].agenda_items.all().values_list('name', flat=True))
                print(inter_c)
                print(ais[0].session.id)
                if inter_c == c1:
                    cc+=1
                    sessions.append(ais[0].session.id)
                    valid_to = s2[0].created_at
                    print('UPDATE')
                    for s in s1:
                        s.valid_to=valid_to
                        s.save()
                    print 'UPDATED', s1.count()
                if s1[0].content==s2[0].content and s1[2].content==s2[2].content:
                    print list(s1[:5].values_list('content'))
                    print list(s2[:5].values_list('content'))
                    cc+=1
                    sessions.append(ais[0].session.id)
                    print('UPDATE')
                    for s in s1:
                        s.valid_to=valid_to
                        s.save()
                    print 'UPDATED', s1.count()
                print


    votes = find_voters_without_membership()
    for person in votes:
        if person:
            if person[0].voter_id==1462:
                for b in person:
                    #print(b.option)
                    if b.option == "for":
                        print(b.vote.start_time)
                        print b.vote.ballot_set.count()
                        print(b.vote.session, b.vote.name)
                    ss.append(b.vote.session_id)



    cc= 0
    data = []
    for v in Vote.objects.all().order_by("start_time"):
        count = v.ballot_set.count()
        if count == 0:
            continue
        #if count == 151:
        #    continue
        cc+=1
        print count
        data.append((v.start_time, count))



    out=[]
    cc = 0
    prev = None
    for c in data:
        if c[1] == cc:
            pass
        else:
            cc = c[1]
            #if cc != 151:
            out.append(prev)
            out.append(c)
        prev = c

    fd=Membership.objects.earliest("start_time").start_time
    rr=(datetime.now()-fd).days

    for i in range(rr):
        date_ = fd+timedelta(days=i)
        members = Membership.objects.filter(Q(start_time__lte=date_) |
                                Q(start_time=None),
                                Q(end_time__gte=date_) |
                                Q(end_time=None),
                                role='voter',
                                organization_id=199).count()
        print(members)


