from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parladata.models.person import Person
from parlacards.serializers.person import PersonSerializer

from parladata.models.organization import Organization
from parlacards.serializers.organization import OrganizationSerializer, OrganizationMembersSerializer

from parlacards.serializers.common import CommonOrganizationSerializer


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
        serializer = PersonSerializer(person, context={'date': request.card_date})
        return Response(serializer.data)


class Voters(APIView):
    '''
    Show a list of all MPs belonging to an organization.
    '''

    def get(self, request, format=None):
        organization = Organization.objects.filter(id=request.card_id).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonSerializer(organization.query_voters(date=request.card_date), many=True, context={'date': request.card_date})
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
        serializer = OrganizationSerializer(organization, context={'date': request.card_date})
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
        serializer = OrganizationMembersSerializer(organization, context={'date': request.card_date})
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
        
        serializer = CommonOrganizationSerializer(organization.query_parliamentary_groups(request.card_date), many=True, context={'date': request.card_date})
        return Response(serializer.data)
