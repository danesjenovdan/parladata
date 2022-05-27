import pytest

from parladata.models.organization import Organization
from parladata.models.person import Person
from parladata.models.common import Mandate

@pytest.fixture
def main_organization():
    return Organization.objects.order_by('id').first()

@pytest.fixture
def mandate():
    return Mandate.objects.first()

@pytest.fixture
def first_person(main_organization):
    return main_organization.query_voters().order_by('id').first()

@pytest.fixture
def second_person(main_organization):
    return main_organization.query_voters().order_by('id')[2]

@pytest.fixture
def last_person(main_organization):
    return main_organization.query_voters().order_by('id').last()

@pytest.fixture
def first_group(main_organization):
    return main_organization.query_parliamentary_groups().order_by('id').first()

@pytest.fixture
def second_group(main_organization):
    return main_organization.query_parliamentary_groups().order_by('id')[2]

@pytest.fixture
def last_group(main_organization):
    return main_organization.query_parliamentary_groups().order_by('id').last()

@pytest.fixture
def first_session(main_organization):
    return main_organization.sessions.first()
