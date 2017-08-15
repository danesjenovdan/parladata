from parladata.models import *
from rest_framework import serializers, viewsets

# Serializers define the API representation.
class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person

# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer