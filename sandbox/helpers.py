from django.db.models import Count

from parladata.models import Speech, Question, Vote, Membership, Organization, Ballot
from parladata.utils import parseRecipient
from django.db.models import Q

from datetime import datetime
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
    mems = Membership.objects.filter(person_id=person_id,
                                     organization__classification__in=PS_NP)
    print mems
    for mem in mems:
        start_time, end_time = getStartEndTime(mem)
        ballots = Ballot.objects.filter(voter_id=person_id,
                                        vote__start_time__gte=start_time,
                                        vote__start_time__lte=end_time)
        print list(set(list(ballots.values_list("voterparty", flat=True))))
        ballots.update(voterparty=mem.organization)


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
                                      organization__classification__in=PS_NP)

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
        speeches.update(party=mem.organization)


def test_ministers_memberships(person_id):
    party = Membership.objects.filter(person_id=person_id,
                                      organization__classification__in=PS_NP)

    ministry = Membership.objects.filter(person_id=person_id,
                                         organization__classification='ministrstvo',
                                         role='minister')
    mems = list(party) + list(ministry)
    mems = sorted(mems, key=lambda x: x.start_time)
    for i, mem in enumerate(mems):
        if i+1 < len(mems):
            if mem.end_time > mems[i+1].start_time:
                print mem, mems[i+1], "membershipa se prekrivata"

