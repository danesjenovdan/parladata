
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User

from parladata.models import (
    Organization, OrganizationMembership, Person, Membership, Speech, Question, Motion, Vote, Ballot, Area, Session, Law
)

from oauth2_provider.models import Application
from datetime import datetime, timedelta

import os
import requests

class Command(BaseCommand):
    help = 'Download croatian database'

    def handle(self, *args, **options):
        self.stdout.write('\n')
        self.stdout.write('Setting minimal setup')
        start_time = datetime(day=1, month=1, year=2020)

        bd = datetime(day=1, month=1, year=1968)

        area = Area(
            name='Center',
            calssification='district')
        area.save()

        dz = Organization(
            _name='DZ',
            classification='dz')
        dz.save()

        coalition = Organization(
            _name='Coalition',
            classification='coalition',
            _acronym='coal',
            is_coalition=1)
        coalition.save()

        opposition = Organization(
            _name='Opposition',
            classification='opposition',
            _acronym='oppo',
            is_coalition=-1)
        opposition.save()

        coal_party = Organization(
            _name='Party from coalition',
            name_parser='Party from coalition',
            gov_id='13',
            classification='pg',
            _acronym='PFC')
        coal_party.save()

        oppo_party = Organization(
            _name='Party from opposition',
            name_parser='Party from opposition',
            gov_id='12',
            classification='pg',
            _acronym='PFO')
        oppo_party.save()

        OrganizationMembership(
            organization=coalition,
            parent=coal_party,
            start_time=start_time
        ).save()

        OrganizationMembership(
            organization=opposition,
            parent=oppo_party,
            start_time=start_time
        ).save()

        person_pfc_1 = Person(
            name='Ivan Coalition',
            name_parser='Ivan Coalition',
            previous_occupation='CEO',
            education='Master of economics',
            education_level=8,
            mandates=3,
            preferred_pronoun='he',
            date_of_birth=bd,
            gov_id='1',
            number_of_voters=100)
        person_pfc_1.save()
        person_pfc_1.districts.add(area)

        person_pfc_2 = Person(
            name='Marjeta Coalition',
            name_parser='Marjeta Coalition',
            previous_occupation='CTO',
            education='PhD',
            education_level=9,
            mandates=1,
            preferred_pronoun='she',
            date_of_birth=bd,
            gov_id='2',
            number_of_voters=200)
        person_pfc_2.save()
        person_pfc_2.districts.add(area)

        person_pfo_1 = Person(
            name='Maja Oppostion',
            name_parser='Maja Oppostion',
            previous_occupation='MTM',
            education='???',
            education_level=7,
            mandates=1,
            preferred_pronoun='she',
            date_of_birth=bd,
            gov_id='3',
            number_of_voters=300)
        person_pfo_1.save()
        person_pfo_1.districts.add(area)

        Membership(
            role='voter',
            person=person_pfc_1,
            organization=dz,
            on_behalf_of=coal_party,
            start_time=start_time).save()

        Membership(
            role='voter',
            person=person_pfc_2,
            organization=dz,
            on_behalf_of=coal_party,
            start_time=start_time).save()

        Membership(
            role='voter',
            person=person_pfo_1,
            organization=dz,
            on_behalf_of=oppo_party,
            start_time=start_time).save()

        Membership(
            role='president',
            person=person_pfc_1,
            organization=coal_party,
            on_behalf_of=None,
            start_time=start_time).save()

        Membership(
            role='deputy',
            person=person_pfc_2,
            organization=coal_party,
            on_behalf_of=None,
            start_time=start_time).save()

        Membership(
            role='president',
            person=person_pfo_1,
            organization=oppo_party,
            on_behalf_of=None,
            start_time=start_time).save()

        session = Session(
            name='Session 1.',
            start_time=start_time,
            organization=dz,
            in_review=False

        )
        session.save()
        session.organizations.add(dz)

        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_1,
            party=coal_party,
            start_time=start_time + timedelta(minutes=5),
            order=1,
            session=session
        )
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_2,
            party=coal_party,
            start_time=start_time + timedelta(minutes=15),
            order=2,
            session=session
        )
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_1,
            party=coal_party,
            start_time=start_time + timedelta(minutes=25),
            order=3,
            session=session
        )
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfo_1,
            party=oppo_party,
            start_time=start_time + timedelta(minutes=35),
            order=4,
            session=session
        )

        motion = Motion(
            text='Voting for president',
            date=start_time,
            session=session,
            organization=dz,
            result='1',
            epa='EPA-1'
        )
        motion.save()
        vote = Vote(
            name='Voting for president',
            motion=motion,
            session=session,
            start_time=start_time + timedelta(minutes=35),
            result='1',
            epa='EPA-1'
        )
        vote.save()

        Ballot(
            vote=vote,
            voter=person_pfc_1,
            voterparty=coal_party,
            option='for'
        ).save()
        Ballot(
            vote=vote,
            voter=person_pfc_2,
            voterparty=coal_party,
            option='for'
        ).save()
        Ballot(
            vote=vote,
            voter=person_pfo_1,
            voterparty=oppo_party,
            option='against'
        ).save()

        question = Question(
            session=session,
            date=start_time,
            date_of_answer=start_time,
            title='Why we need to work on the first day?',
            recipient_text='Prime minister'
        )
        question.save()
        question.authors.add(person_pfo_1)
        question.author_orgs.add(oppo_party)

        Law(
            session=session,
            text='Voting for president',
            epa='EPA-1',
            classification='act',
            result='enacted',
            date=start_time,
            procedure_ended=True
        ).save()
        Law(
            session=session,
            text='Voting for dinner.',
            epa='EPA-1',
            classification='act',
            result='',
            status='in_procedure',
            procedure_ended=False
        ).save()

        user = models.User(
            first_name='parlauser',
            username='parlauser',
            email='test@test.com',
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        user.save()
        user.set_password('password')
        user.save()

        Application(
            client_id='kIZWxeodL29mfaKSIGQWPUuuck8CXv3m58XuJ8Y7',
            client_secret='54pWmrpj1y9FiwkUDofjeP4B5tbLQ4wW6F2wqsMT3JuQN4ApIqcveKlzOC1laQIJp8JpVi99EheHCkumEJ0o81J9f2uHK3eXjUdxprzDnWlsTuZM6cgv1Eo35KSr7Mfg',
            user=user,
            client_type='confidential',
            authorization_grant_type= 'password',
            name='client'
        ).save()
