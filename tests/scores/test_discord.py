import pytest

from parlacards.scores.discord import (
    calculate_group_discord
)

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_group,
    second_group,
    last_group,
):
    # group
    discord = calculate_group_discord(first_group)
    assert discord == 8.75

    discord = calculate_group_discord(second_group)
    assert discord == 30.000000000000007

    discord = calculate_group_discord(last_group)
    assert discord == 8.804347826086955
