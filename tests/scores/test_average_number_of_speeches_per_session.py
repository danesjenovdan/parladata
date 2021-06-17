import pytest

from parlacards.scores.avg_number_of_speeches_per_session import calculate_person_avg_number_of_speeches

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_person_avg_number_of_speeches(
    first_person,
    second_person,
    last_person
):
    avg_number_of_speeches = calculate_person_avg_number_of_speeches(first_person)
    assert avg_number_of_speeches == 3.0

    avg_number_of_speeches = calculate_person_avg_number_of_speeches(second_person)
    assert avg_number_of_speeches == 0

    avg_number_of_speeches = calculate_person_avg_number_of_speeches(last_person)
    assert avg_number_of_speeches == 12.5
