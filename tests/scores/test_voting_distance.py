import pytest

from parlacards.scores.voting_distance import calculate_voting_distance

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_person,
    second_person,
    last_person
):
    voting_distance = calculate_voting_distance(first_person, second_person)
    assert voting_distance == 3.872983346207417

    voting_distance = calculate_voting_distance(second_person, first_person)
    assert voting_distance == 3.872983346207417

    voting_distance = calculate_voting_distance(first_person, last_person)
    assert voting_distance == 2.449489742783178

    voting_distance = calculate_voting_distance(second_person, last_person)
    assert voting_distance == 3.872983346207417
