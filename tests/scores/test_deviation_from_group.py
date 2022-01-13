import pytest

from parlacards.scores.deviation_from_group import calculate_deviation_from_group

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_deviation_from_group(
    first_person,
    second_person,
    last_person,
    main_organization
):
    deviation = calculate_deviation_from_group(first_person, main_organization)
    assert deviation == 0

    deviation = calculate_deviation_from_group(second_person, main_organization)
    assert deviation == 0

    deviation = calculate_deviation_from_group(last_person, main_organization)
    assert deviation == 32.432432432432435
