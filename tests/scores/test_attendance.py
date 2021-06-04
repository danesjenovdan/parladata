import pytest

from parlacards.scores.attendance import calculate_person_vote_attendance

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_person_vote_attendance(
    first_person,
    second_person,
    last_person
):
    attendance = calculate_person_vote_attendance(first_person)
    assert attendance == 96.15384615384616

    attendance = calculate_person_vote_attendance(second_person)
    assert attendance == 65.38461538461539

    attendance = calculate_person_vote_attendance(last_person)
    assert attendance == 96.15384615384616
