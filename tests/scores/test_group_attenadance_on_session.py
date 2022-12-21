import pytest

from parlacards.scores.session_attendance import calculate_session_vote_attendance

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_session_vote_attendance(
    first_session,
    first_group,
    second_group,
    last_group
):
    attendance = calculate_session_vote_attendance(first_session, first_group)
    assert attendance == 46.55172413793103

    attendance = calculate_session_vote_attendance(first_session, second_group)
    assert attendance == 32.18390804597701

    attendance = calculate_session_vote_attendance(first_session, last_group)
    assert attendance == 93.25337331334333

