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
    main_organization,
):
    # group
    discord = calculate_group_discord(first_group, main_organization)
    assert discord == 2.9411764705882355

    discord = calculate_group_discord(second_group, main_organization)
    assert discord == 27.619047619047617

    discord = calculate_group_discord(last_group, main_organization)
    assert discord == 26.753246753246753
