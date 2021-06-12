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
    assert voting_distance == 3.872983346207417

    voting_distance = calculate_voting_distance(second_person, first_person)
    assert voting_distance == 3.872983346207417

    voting_distance = calculate_voting_distance(first_person, last_person)
    assert voting_distance == 2.449489742783178

    voting_distance = calculate_voting_distance(second_person, last_person)
    assert voting_distance == 3.872983346207417

    # group
    group_voting_distances = calculate_group_voting_distance(first_group, main_organization)
    assert len(group_voting_distances) == 42
    assert group_voting_distances[29] == 2.0
    assert group_voting_distances[12] == 4.47213595499958
    assert group_voting_distances[41] == 3.7416573867739413

    # THIS IS NOT USED BUT POSSIBLY INTERESTING
    voting_distance = calculate_voting_distance_between_groups(first_group, last_group)
    assert voting_distance == 2

    voting_distance = calculate_voting_distance_between_groups(last_group, first_group)
    assert voting_distance == 2

    voting_distance = calculate_voting_distance_between_groups(first_group, second_group)
    assert voting_distance == 1.4142135623730951

    voting_distance = calculate_voting_distance_between_groups(second_group, last_group)
    assert voting_distance == 1
