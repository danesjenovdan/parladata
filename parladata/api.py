from parladata.models import *
from rest_framework import serializers, viewsets

# Serializers define the API representation.
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session

# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    fields = '__all__'
    #http_method_names=['post', 'delete', 'update', 'options']

class SessionView(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    fields = '__all__'