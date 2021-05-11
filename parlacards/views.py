from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from parladata.models import Person
from parlacards.serializers import PersonSerializer

from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.db.models import Q

class PersonInfo(APIView):
    """
    Show basic person info.
    """
    def get(self, request, format=None):
        # get the request parameters
        person_id = request.GET.get('id', None)
        date_string = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # if no permanent_id was supplied, return
        if not person_id:
            content = {'error': '`person_id` is required.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # try parsing the date
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
        # if the date could not be parsed, return
        except ValueError as e:
            content = {'error': f'Can not parse date. Please use the following format: {datetime.now().strftime("%Y-%m-%d")}'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        
        person = Person.objects.filter(id=person_id).first()

        # if no people were found, return
        if not person:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer_context = dict(
            date=date
        )
        serializer = PersonSerializer(person, context=serializer_context)
        return Response(serializer.data)
