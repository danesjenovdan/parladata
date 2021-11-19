from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from parladata.models import (
    Motion, Vote, Organization, OrganizationMembership, Person, Session, Area, Law, Link,
    Mandate, PersonMembership, Speech, OrganizationEmail, AgendaItem, Ballot, Question, Document
)
from parladata.models.versionable_properties import (
    PersonPreviousOccupation, PersonName, PersonEducation, PersonNumberOfMandates, PersonEmail,
    PersonPreferredPronoun, PersonNumberOfVoters, PersonNumberOfPoints, OrganizationName,
    OrganizationAcronym, PersonEducationLevel
)
from parlacards.models import PersonTfidf, GroupTfidf, SessionTfidf
from taggit.models import Tag


class Command(BaseCommand):
    help = 'Set motion tags'

    def handle(self, *args, **options):
        self.stdout.write('Creating editor group')

        self.basc_options = [('change_', 'Can change '), ('view_', 'Can view ')]
        self.options = [('add_', 'Can add '), ('change_', 'Can change '), ('view_', 'Can view '), ('delete_', 'Can delete ')]

        models = [
            Motion, Vote, Organization, OrganizationMembership, Person, Session, PersonPreviousOccupation,
            PersonName, PersonEducation, PersonNumberOfMandates, PersonEmail, PersonPreferredPronoun,
            PersonNumberOfVoters, PersonNumberOfPoints, OrganizationName, OrganizationEmail, OrganizationAcronym,
            PersonTfidf, GroupTfidf, SessionTfidf, Area, Law, Link, Mandate, PersonEducationLevel,
            PersonMembership, Speech, Tag, AgendaItem, Ballot, Question, Document
        ]

        editor, created = Group.objects.get_or_create(name='editor')

        for model in models:
            print(model)
            ct = ContentType.objects.get_for_model(model)
            permissions = self.get_permissions(model.__name__.lower(), ct, self.options)
            editor.permissions.add(*permissions)


    def get_permissions(self, name, ct, options):
        permissions = []
        for option in options:
            print(f'{option[0]}{name}')
            permissions.append(Permission.objects.get(
                content_type_id=ct.id,
                codename=f'{option[0]}{name}')
            )
        return permissions





