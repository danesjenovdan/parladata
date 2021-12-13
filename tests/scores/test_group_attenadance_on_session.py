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
    assert attendance == 85.71428571428571

    attendance = calculate_session_vote_attendance(first_session, second_group)
    assert attendance == 30.952380952380953

    attendance = calculate_session_vote_attendance(first_session, last_group)
    assert attendance == 96.5909090909091

