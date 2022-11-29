import pytest

from parlacards.scores.voting_distance import (
    calculate_voting_distance,
    calculate_group_voting_distance,
    calculate_voting_distance_between_groups
)

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_person,
    second_person,
    last_person,
    first_group,
    second_group,
    last_group,
    main_organization
): 
    # person
    voting_distance = calculate_voting_distance(first_person, second_person)
    assert voting_distance == 0.0

    voting_distance = calculate_voting_distance(second_person, first_person)
    assert voting_distance == 0.0

    voting_distance = calculate_voting_distance(first_person, last_person)
    assert voting_distance == 29.629629629629626

    voting_distance = calculate_voting_distance(second_person, last_person)
    assert voting_distance == 0.0

    # group
    group_voting_distances = calculate_group_voting_distance(first_group, main_organization)
    assert len(group_voting_distances) == 39
    assert group_voting_distances[29] == 37.93103448275862
    assert group_voting_distances[12] == 72.0
    assert group_voting_distances[41] == 33.33333333333333

    # THIS IS NOT USED BUT POSSIBLY INTERESTING
    voting_distance = calculate_voting_distance_between_groups(first_group, last_group)
    assert voting_distance == 5.744562646538029

    voting_distance = calculate_voting_distance_between_groups(last_group, first_group)
    assert voting_distance == 5.744562646538029

    voting_distance = calculate_voting_distance_between_groups(first_group, second_group)
    assert voting_distance == 3.7416573867739413

    voting_distance = calculate_voting_distance_between_groups(second_group, last_group)
    assert voting_distance == 2.23606797749979
