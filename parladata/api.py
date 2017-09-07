from parladata.models import *
from rest_framework import serializers, viewsets

# Serializers define the API representation.
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization

class SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speech

class MotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion


class VoteSerializer(serializers.ModelSerializer):
    """unedit = serializers.SerializerMethodField('unedited')
    def unedited(self):
        gs = Vote.objects.filter(result=None, tags=None)
        serializer = LikeSerializer(instance=gs, many=True)
        return serializer.data"""
    class Meta:
        model = Vote


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link




# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    fields = '__all__'


class SessionView(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    fields = '__all__'


class OrganizationView(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    fields = '__all__'


class SpeechView(viewsets.ModelViewSet):
    queryset = Speech.objects.all()
    serializer_class = SpeechSerializer
    fields = '__all__'



class MotionView(viewsets.ModelViewSet):
    queryset = Motion.objects.all()
    serializer_class = MotionSerializer
    fields = '__all__'


class VoteFilter(viewsets.ModelViewSet):
    queryset = Vote.objects.filter(result='-', tags=None)
    serializer_class = VoteSerializer
    fields = '__all__'

class VoteView(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    fields = '__all__'


class BallotView(viewsets.ModelViewSet):
    queryset = Ballot.objects.all()
    serializer_class = BallotSerializer
    fields = '__all__'


class LinkView(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    fields = '__all__'