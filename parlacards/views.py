from datetime import datetime

from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parladata.models.person import Person
from parlacards.serializers.person import PersonSerializer

from parladata.models.organization import Organization
from parlacards.serializers.organization import OrganizationSerializer, OrganizationMembersSerializer, OrganizationVocabularySizeSerializer

from parladata.models.common import Mandate
from parlacards.serializers.session import SessionSerializer

from parladata.models.legislation import Law
from parlacards.serializers.legislation import LegislationSerializer

from parlacards.serializers.person import (
    PersonVocabularySizeSerializer,
    PersonBallotSerializer,
    PersonMostEqualVoterSerializer,
    PersonLeastEqualVoterSerializer,
)

from parlacards.serializers.common import CommonPersonSerializer, CommonOrganizationSerializer


class PersonInfo(APIView):
    """
    Show basic person info.
    """
    def get(self, request, format=None):
        # find the person and if no people were found return
        person = Person.objects.filter(id=request.card_id).first()
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # serialize the results and return
        serializer = PersonSerializer(
            person,
            context={'date': request.card_date}
        )
        return Response(serializer.data)


class Voters(APIView):
    '''
    Show a list of all MPs belonging to an organization.
    '''

    def get(self, request, format=None):
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonSerializer(
            organization.query_voters(date=request.card_date),
            many=True,
            context={'date': request.card_date}
        )
        return Response(serializer.data)

class OrganizationInfo(APIView):
    """
    Show basic info of organization.
    """
    def get(self, request, format=None):
        # find the organization and if none were found return
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # serialize the results and return
        serializer = OrganizationSerializer(
            organization,
            context={'date': request.card_date}
        )
        return Response(serializer.data)


class OrganizationMembers(APIView):
    """
    Show basic info of organization.
    """
    def get(self, request, format=None):
        # find the organization and if none were found return
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # serialize the results and return
        serializer = OrganizationMembersSerializer(
            organization,
            context={'date': request.card_date}
        )
        return Response(serializer.data)


class ParliamentaryGroups(APIView):
    '''
    List parties in an organization.
    '''
    def get(self, request, format=None):
        # find the organization and if none were found return
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommonOrganizationSerializer(
            organization.query_parliamentary_groups(date=request.card_date),
            many=True,
            context={'date': request.card_date}
        )
        return Response(serializer.data)


class Sessions(APIView):
    '''
    List sessions in a mandate.
    '''
    def get(self, request, format=None):
        # find the mandate and if none were found return
        mandate = Mandate.objects.filter(id=request.card_id).first()
        if not mandate:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = SessionSerializer(
            mandate.sessions.filter(
                Q(start_time__lte=request.card_date) | Q(start_time__isnull=True)
            ),
            many=True,
            context={'date': request.card_date})
        return Response(serializer.data)


class Legislation(APIView):
    '''
    List legislation in a mandate.
    '''
    def get(self, request, format=None):
        # find the mandate and if none were found return
        mandate = Mandate.objects.filter(id=request.card_id).first()
        if not mandate:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = LegislationSerializer(
            Law.objects.filter(
                Q(datetime__lte=request.card_date) | Q(datetime__isnull=True),
                session__mandate=mandate,
            ),
            many=True,
            context={'date': request.card_date})
        return Response(serializer.data)


class VocabularySize(APIView):
    '''
    A person's vocabulary size.
    '''
    def get(self, request, format=None):
        # find the person and if none were found return
        person = Person.objects.filter(id=request.card_id).first()
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PersonVocabularySizeSerializer(
            person,
            context={'date': request.card_date},
        )
        return Response(serializer.data)


class OrganizationVocabularySize(APIView):
    '''
    An organization's vocabulary size.
    '''
    def get(self, request, format=None):
        # find the organization and if none were found return
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrganizationVocabularySizeSerializer(
            organization,
            context={'date': request.card_date},
        )
        return Response(serializer.data)


class Ballots(APIView):
    '''
    A person's ballots.
    '''
    def get(self, request, format=None):
        # find the person and if none were found return
        person = Person.objects.filter(id=request.card_id).first()
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonBallotSerializer(
            person,
            context={'date': request.card_date},
        )
        return Response(serializer.data)


class PersonMostEqualVoters(APIView):
    '''
    A person's most equal voters.
    '''
    def get(self, request, format=None):
        # find the person and if none were found return
        person = Person.objects.filter(id=request.card_id).first()
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonMostEqualVoterSerializer(
            person,
            context={'date': request.card_date},
        )
        return Response(serializer.data)


class PersonLeastEqualVoters(APIView):
    '''
    A person's most equal voters.
    '''
    def get(self, request, format=None):
        # find the person and if none were found return
        person = Person.objects.filter(id=request.card_id).first()
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonLeastEqualVoterSerializer(
            person,
            context={'date': request.card_date},
        )
        return Response(serializer.data)
