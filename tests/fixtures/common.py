import pytest

from parladata.models.organization import Organization
from parladata.models.person import Person
from parladata.models.common import Mandate

from datetime import datetime, timedelta

@pytest.fixture
def main_organization():
    return Organization.objects.order_by('id').first()

@pytest.fixture
def first_mandate():
    return Mandate.objects.order_by('id').first()

@pytest.fixture
def ending_date_of_first_mandate(first_mandate):
    return first_mandate.ending - timedelta(days=1)



@pytest.fixture
def first_person(main_organization, ending_date_of_first_mandate):
    return main_organization.query_voters(ending_date_of_first_mandate).order_by('id').first()

@pytest.fixture
def second_person(main_organization, ending_date_of_first_mandate):
    return main_organization.query_voters(ending_date_of_first_mandate).order_by('id')[2]

@pytest.fixture
def last_person(main_organization, ending_date_of_first_mandate):
    return main_organization.query_voters(ending_date_of_first_mandate).order_by('id').last()

@pytest.fixture
def first_group(main_organization, ending_date_of_first_mandate):
    return main_organization.query_parliamentary_groups(ending_date_of_first_mandate).order_by('id').first()

@pytest.fixture
def second_group(main_organization, ending_date_of_first_mandate):
    return main_organization.query_parliamentary_groups(ending_date_of_first_mandate).order_by('id')[2]

@pytest.fixture
def last_group(main_organization, ending_date_of_first_mandate):
    return main_organization.query_parliamentary_groups(ending_date_of_first_mandate).order_by('id').last()

@pytest.fixture
def first_session(main_organization):
    return main_organization.sessions.first()



# fixtures for views
@pytest.fixture
def first_mandate_params():
    return {
        'id': '1',
        'date': '2019-11-29',
    }

@pytest.fixture
def current_mandate_params():
    return {
        'id': '2',
    }

@pytest.fixture
def current_root_org():
    return {
        'id': '48',
    }

@pytest.fixture
def first_root_org():
    return {
        'id': '1',
    }

@pytest.fixture
def first_mandate_party():
    return {
        'id': '19',
    }

@pytest.fixture
def all_mandate_party():
    return {
        'id': '20',
    }

@pytest.fixture
def first_mandate_member():
    return {
        'id': '240',
    }

@pytest.fixture
def all_mandate_member():
    return {
        'id': '245',
    }
