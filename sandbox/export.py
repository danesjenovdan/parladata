# -*- coding: utf-8 -*-
import csv
import sys


PS = ['poslanska skupina']

def dictToCSV(data, file_name):
    with open('exports/' + file_name, 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)

        for key, value in list(data.items()):
            if type(value) == list:
                e_data = value
            else:
                e_data = [value]

            csvwriter.writerow([key] + e_data)
    return 'saved in exports/' + file_name


def listToCSV(data, file_name):
    with open('exports/' + file_name, 'w') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter='\t',
                               quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)

        for value in data:
            if type(value) == list:
                e_data = value
            elif type(value) == tuple:
                e_data = list(value)
            else:
                e_data = [value]
            csvwriter.writerow(e_data)
    return 'saved in exports/' + file_name


def getAmendment():
    data = [['PG', 'status', 'link']]
    parliamentaryGroups = Organization.objects.filter(classification__in=PS)
    acronyms = list(set(list(parliamentaryGroups.values_list('acronym', flat=True))))
    amandmas = Vote.objects.filter(name__icontains='amandma')
    for acronym in acronyms:
        temp_amandmas = amandmas.filter(name__icontains="["+acronym).values_list("session_id", "id", "motion__result")
        pg_amandmas = [list(map(str, i))
                       for i
                       in temp_amandmas]
        for amandma in pg_amandmas:
            data.append([acronym, amandma[2], 'https://parlameter.si/seja/glasovanje/' + '/'.join(amandma[:2])])
    listToCSV(data, 'amandmaji.csv')


def num_speeches_and_ballots_opts():
    for p in pp:
        person_data = []
        person_data.append(p)
        person_data.append(Speech.getValidSpeeches(datetime.now()).filter(speaker=p).count())
        options = Counter(Ballot.objects.filter(voter=p).values_list("option", flat=True))
        person_data.append(options["for"])
        person_data.append(options["against"])
        person_data.append(options["abstain"])
        person_data.append(options["absent"])
        data.append(person_data)


def get_whole_mandate_members():

    membership = Membership.objects.filter(organization__classification__in=PS_NP)
    people = list(set(list(membership.values_list('person', flat=True))))
    const_mems = membership.filter(start_time=min(membership.values_list("start_time", flat=True)), end_time=None)

    start_mems = membership.filter(start_time=min(membership.values_list("start_time", flat=True)))

    jumpers = start_mems.exclude(id__in=const_mems)

    jump_persons = jumpers.values_list("person", flat=True).distinct("person")

    data = []
    for p in jump_persons:
        is_valid = True
        mems = Membership.objects.filter(person_id=p, organization__classification__in=PS_NP).order_by("start_time")
        if mems.filter(end_time=None):
            print((p, "je zacel"))
            # This members is stil member
            end_time = mems[0].start_time
            print(end_time)
            for m in mems:
                if (m.start_time - end_time).days > 1:
                    is_valid = False
                end_time = m.end_time
            if is_valid:
                data.append(p)
        else:
          print([mem.end_time for mem in mems])
    return data


def export_people():
    data = [['id',
             'polno ime',
             'prejsna zaposlitev',
             'izobrazba',
             'stopnja izobrazbe',
             'st. mandatov',
             'email',
             'spol',
             'datum rojstva',
             'gov_id',
             'okraj',
             'st. volilcev',
             'poslanska skupina']]
    for person in Person.objects.all():
        mem = Membership.objects.filter(person=person)
        data.append([
            person.id,
            person.name,
            person.previous_occupation,
            person.education,
            person.education_level,
            person.mandates,
            person.email,
            person.gender,
            person.birth_date,
            person.gov_id,
            list(person.districts.all().values_list("name", flat=True)),
            person.voters,
            mem[0].organization.acronym if mem else '',
        ])

    listToCSV(data, 'poslanci-VIII.csv')

def export_questions():
    out_data = [['text', 'date', 'author', 'author_org', 'recipient', 'recipient_org', 'doc']]
    for q in Question.objects.all():
        out_data.append([
            q.title,
            q.date.isoformat(),
            ' & '.join(list(q.authors.values_list('name', flat=True))),
            ' & '.join(list(q.author_orgs.values_list('_acronym', flat=True))),
            ' & '.join(list(q.recipient_person.values_list('name', flat=True))),
            ' & '.join(list(q.recipient_organization.values_list('_name', flat=True))),
            ' '.join(list(q.links.values_list('url', flat=True))),
        ])


def getVotesByHand():
    out_data = [['session', 'text', 'hand vote']]
    for vote in Vote.objects.all():
        out_data.append([
            vote.session.name,
            vote.name,
            bool(vote.counter)
        ])
    listToCSV(out_data, 'votes-hand.csv')



def get_votes_array(votes):
    return [[vote.motion, vote.result, vote.start_time.isoformat(), vote.session.name] for vote in votes]

# for l in ll:
#     votes = Vote.objects.filter(epa=l.epa).order_by('start_time')
#     print(l.epa, l.text, l.result)
