from datetime import datetime

from django.db.models import Q

from parladata.models.question import Question

from parlacards.models import PersonNumberOfQuestions, GroupNumberOfQuestions

from parlacards.scores.common import get_dates_between, get_fortnights_between


# People
def calculate_number_of_questions_from_person(person, timestamp=datetime.now()):
    return Question.objects.filter(
        authors=person,
        timestamp__lte=timestamp
    ).count()

def save_number_of_questions_from_person(person, playing_field, timestamp=datetime.now()):
    PersonNumberOfQuestions(
        person=person,
        value=calculate_number_of_questions_from_person(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_number_of_questions(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_number_of_questions_from_person(person, playing_field, timestamp)

def save_people_number_of_questions_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_number_of_questions(playing_field, timestamp=day)

def save_sparse_people_number_of_questions_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_number_of_questions(playing_field, timestamp=day)


# Groups
def calculate_group_number_of_question(group, playing_field, timestamp=datetime.now()):
    """
    Returns question count of group
    """
    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list('member_id', flat=True).distinct('member_id')

    questions = Question.objects.none()

    for member_id in member_ids:
        member_questions = Question.objects.filter(
            timestamp__lte=timestamp,
            authors__id=member_id,
        )

        member_memberships = memberships.filter(
            member__id=member_id
        ).values(
            'start_time',
            'end_time'
        )
        q_objects = Q()
        for membership in member_memberships:
            q_params = {}
            if membership['start_time']:
                q_params['timestamp__gte'] = membership['start_time']
            if membership['end_time']:
                q_params['timestamp__lte'] = membership['end_time']
            q_objects.add(
                Q(**q_params),
                Q.OR
            )

        questions = questions.union(member_questions.filter(q_objects))

    return questions.count()

def save_group_number_of_questions_for_group(group, playing_field, timestamp=datetime.now()):
    questions_count = calculate_group_number_of_question(group, playing_field, timestamp)

    GroupNumberOfQuestions(
        group=group,
        value=questions_count,
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_group_number_of_questions(playing_field, timestamp=datetime.now()):
    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_number_of_questions_for_group(group, playing_field, timestamp)

def save_group_number_of_questions_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_group_number_of_questions(playing_field, timestamp=day)

def save_sparse_group_number_of_questions_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_group_number_of_questions(playing_field, timestamp=day)
