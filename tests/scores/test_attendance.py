import pytest

from parlacards.scores.attendance import (
    calculate_person_vote_attendance,
    calculate_group_vote_attendance
)

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_person_vote_attendance(
    first_person,
    second_person,
    last_person
):
    attendance = calculate_person_vote_attendance(first_person)
    assert attendance == 91.89189189189189

    attendance = calculate_person_vote_attendance(second_person)
    assert attendance == 0

    attendance = calculate_person_vote_attendance(last_person)
    assert attendance == 89.1891891891892


@pytest.mark.django_db()
def test_calculate_group_vote_attendance(
    first_group,
    last_group
):
    attendance = calculate_group_vote_attendance(first_group)
    assert attendance == 75

    attendance = calculate_group_vote_attendance(last_group)
    assert attendance == 75.0
