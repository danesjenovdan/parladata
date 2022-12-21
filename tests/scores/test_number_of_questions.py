import pytest

from parlacards.scores.number_of_questions import calculate_number_of_questions_from_person

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_number_of_questions_from_person(
    first_person,
    second_person,
    last_person
):
    number_of_questions = calculate_number_of_questions_from_person(first_person)
    assert number_of_questions == 0

    number_of_questions = calculate_number_of_questions_from_person(second_person)
    assert number_of_questions == 1

    number_of_questions = calculate_number_of_questions_from_person(last_person)
    assert number_of_questions == 0
