import pytest

from django.core.management import call_command

from parladata.models.organization import Organization
from parladata.models.person import Person

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/fixtures/test_db.json')

@pytest.fixture(scope='session')
def main_org(django_db_blocker):
    with django_db_blocker.unblock():
        return Organization.objects.first()

@pytest.fixture(scope='session')
def first_person(main_org, django_db_blocker):
    with django_db_blocker.unblock():
        return main_org.query_voters().first()

@pytest.fixture(scope='session')
def second_person(main_org, django_db_blocker):
    with django_db_blocker.unblock():
        return main_org.query_voters()[2]

@pytest.fixture(scope='session')
def last_person(main_org, django_db_blocker):
    with django_db_blocker.unblock():
        return main_org.query_voters().last()
