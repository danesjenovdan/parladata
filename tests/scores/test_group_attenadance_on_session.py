import pytest

from parlacards.scores.session_attendance import calculate_session_vote_attendance

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_person_monthly_vote_attendance(
    first_session,
    first_group,
    second_group,
    last_group
):
    attendance = calculate_session_vote_attendance(first_session, first_group)
    assert attendance == 75.0

    attendance = calculate_session_vote_attendance(first_session, second_group)
    assert attendance == 66.66666666666667

    attendance = calculate_session_vote_attendance(first_session, last_group)
    assert attendance == 75.0

