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
    assert discord == 2.7027027027027026

    discord = calculate_group_discord(second_group)
    assert discord == 27.927927927927932

    discord = calculate_group_discord(last_group)
    assert discord == 25.55282555282555
