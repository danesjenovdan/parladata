from datetime import datetime

from parladata.models.question import Question

from parlacards.models import PersonNumberOfQuestions

from parlacards.scores.common import get_dates_between, get_fortnights_between


def calculate_number_of_questions_from_person(person, timestamp=datetime.now()):
    person_question = Question.objects.filter(authors=person, timestamp__lte=timestamp)
    return person_question.count()

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
