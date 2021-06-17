import pytest

from parlacards.scores.monthly_attendance import calculate_person_monthly_vote_attendance

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_person_monthly_vote_attendance(
    first_person,
    second_person,
    last_person,
    main_organization
):
    monthly_attendance = calculate_person_monthly_vote_attendance(first_person, main_organization)
    assert len(monthly_attendance) == 2
    assert sum([attendance['absent'] for attendance in monthly_attendance]) == 3
    assert sum([attendance['abstain'] for attendance in monthly_attendance]) == 7
    assert sum([attendance['for'] for attendance in monthly_attendance]) == 20
    assert sum([attendance['against'] for attendance in monthly_attendance]) == 7
    assert sum([attendance['total'] for attendance in monthly_attendance]) == 37

    monthly_attendance = calculate_person_monthly_vote_attendance(second_person, main_organization)
    assert sum([attendance['absent'] for attendance in monthly_attendance]) == 0
    assert sum([attendance['abstain'] for attendance in monthly_attendance]) == 0
    assert sum([attendance['for'] for attendance in monthly_attendance]) == 0
    assert sum([attendance['against'] for attendance in monthly_attendance]) == 0
    assert sum([attendance['total'] for attendance in monthly_attendance]) == 37

    monthly_attendance = calculate_person_monthly_vote_attendance(last_person, main_organization)
    assert sum([attendance['absent'] for attendance in monthly_attendance]) == 4
    assert sum([attendance['abstain'] for attendance in monthly_attendance]) == 0
    assert sum([attendance['for'] for attendance in monthly_attendance]) == 25
    assert sum([attendance['against'] for attendance in monthly_attendance]) == 8
    assert sum([attendance['total'] for attendance in monthly_attendance]) == 37
