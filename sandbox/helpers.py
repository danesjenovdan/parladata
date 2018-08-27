from django.db.models import Count

from parladata.models import Speech, Question, Vote, Membership, Organization, Ballot, Person
from parladata.utils import parseRecipient
from django.db.models import Q
from django.conf import settings

from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

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
        print Speech.getValidSpeeches(new_year+timedelta(i)).filter(speaker__id=41).count()


def setRecipientsToQuestions():
    questions = Question.objects.all()
    not_a_member = []
    for question in questions:
        text = question.recipient_text
        date = question.date
        recipients = parseRecipient(text, date)
        print recipients, text
        for i, recipient in enumerate(recipients):
            if recipient:
                if recipient['type'] == 'person':
                    print 'save person'
                    question.recipient_person.add(recipient['recipient'])
                elif recipient['type'] == 'org':
                    print 'save org'
                    question.recipient_organization.add(recipient['recipient'])
                elif recipient['type'] == 'post':
                    print 'save post'
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
                                     organization=settings.DZ_ID,
                                     role='voter').exclude(on_behalf_of=None)

    print mems
    for mem in mems:
        start_time, end_time = getStartEndTime(mem)
        ballots = Ballot.objects.filter(voter_id=person_id,
                                        vote__start_time__gte=start_time,
                                        vote__start_time__lte=end_time)
        print list(set(list(ballots.values_list("voterparty", flat=True))))
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
                                      organization=settings.DZ_ID,
                                      role='voter').exclude(on_behalf_of=None)

    ministry = Membership.objects.filter(person_id=person_id,
                                         organization__classification='ministrstvo',
                                         role__in=['minister', 'ministrica'])
    mems = list(party) + list(ministry)
    mems = sorted(mems, key=lambda x: x.start_time)
    print mems
    prev_end = None
    for mem in mems:
        start_time, end_time = getStartEndTime(mem)

        speeches = Speech.objects.filter(speaker_id=person_id,
                                         start_time__gte=start_time,
                                         start_time__lte=end_time)
        speeches.update(party=mem.on_behalf_of)


def test_ministers_memberships(person_id):
    party = Membership.objects.filter(person_id=person_id,
                                      organization=settings.DZ_ID,
                                      role='voter').exclude(on_behalf_of=None)

    ministry = Membership.objects.filter(person_id=person_id,
                                         organization__classification='ministrstvo',
                                         role='minister')
    mems = list(party) + list(ministry)
    mems = sorted(mems, key=lambda x: x.start_time)
    for i, mem in enumerate(mems):
        if i+1 < len(mems):
            if mem.end_time > mems[i+1].start_time:
                print mem, mems[i+1], "membershipa se prekrivata"


def uk_motion_result():
    from collections import *
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


def set_ballot(option):
    dz_org = Organization.objects.filter(id=settings.DZ_ID)[0]
    for vote in Vote.objects.all():
        # get all MPs
        voters = vote.ballot_set.all().values_list('voter', flat=True)
        print(voters.count())
        mems = Membership.objects.filter(organization__classification__in=PS_NP)

        fdate = vote.start_time
        mems = mems.filter(
            Q(start_time__lte=fdate) |
            Q(start_time=None),
            Q(end_time__gte=fdate) |
            Q(end_time=None)
        )
        people = Person.objects.filter(id__in=mems.values_list('person_id', flat=True)).exclude(id__in=voters)
        print(people.count(), "people")
        for person in people:
            Ballot(vote=vote, voter=person, option=option, voterparty=dz_org).save()

def check_person_parser_data():
    fields = ['birth_date', 'gender', 'districts', 'education', 'education_level']
    data = []
    for p in pp:
        missing_data = [i for i in fields if not getattr(p, i)]
        if missing_data:
            data.append({'missing': missing_data, 'person': p.name, 'id': p.id, 'url': 'http://51.15.135.53/data/admin/parladata/person/' + str(p.id) + '/'})
    return data


def getPersonsFromOldParlameter():
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    count = 0
    url = 'https://data.parlameter.si/v1/persons'
    old_people = getDataFromPagerApiDRF(url)
    for person in Person.objects.all():
        old = get_person_by_parser_name(old_people, person.name_parser)
        if old:
            count += 1
            print 'update ', person.name.encode('utf-8'), old['name'].encode('utf-8')
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
            print 'skipp ', person.name.encode('utf-8')

    print count


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
            print d


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

    for i, m in mps.items():
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
    print('source', s_pss, 'dest_org', d_pss)

    dest_org_obj = Organization.objects.get(id=dest_org)

    for ps_m in s_pss:
        print ps_m.person
        person = ps_m.person
        dest_membership = d_pss.filter(person=person)
        if dest_membership:
            if ps_m.end_time == None:
                # check start time and fix it
                if dest_membership[0].end_time == None:
                    print 'Fixing start time', dest_membership[0].start_time, ps_m.start_time
                    dest_membership = dest_membership[0]
                    dest_membership.start_time = ps_m.start_time
                    dest_membership.save()

                else:
                    print('This shit does not work')
            else:
                # add new membership
                print 'copying memberhsip 2'
                ps_m.pk = None
                ps_m.organization = dest_org_obj
                ps_m.save()

        else:
            # add new membership
            print 'copying memberhsip 1', ps_m.start_time, ps_m.end_time
            ps_m.pk = None
            ps_m.organization = dest_org_obj
            ps_m.save()


def create_parliament_memberships(orgs_for_exclude=[]):
    parliament = Organization.objects.get(id=settings.DZ_ID)
    mm = Membership.objects.filter(organization__classification__in=settings.PS_NP).exclude(organization__id__in=orgs_for_exclude)
    for m in mm:
        m.pk = None
        m.on_behalf_of = m.organization
        m.organization = parliament
        m.role = 'voter'
        m.save()