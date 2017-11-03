from parladata.models import *
from taggit.models import Tag
from rest_framework import serializers, viewsets
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from django.db.models import Q
from rest_framework.decorators import detail_route

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

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
    vote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Motion


class VoteSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    results = serializers.SerializerMethodField()
    class Meta:
        model = Vote
    def get_results(self, obj):
        return obj.getResult()


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link


class LawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    fields = '__all__'


class SessionView(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('organization',)
    ordering_fields = ('start_time',)



class LastSessionWithVoteView(SessionView):
    s_id = Vote.objects.latest('start_time').session_id
    queryset = Session.objects.filter(id=s_id)

class OrganizationView(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    fields = '__all__'


class SpeechView(viewsets.ModelViewSet):
    queryset = Speech.objects.all()
    serializer_class = SpeechSerializer
    fields = '__all__'



class MotionView(viewsets.ModelViewSet):
    queryset = Motion.objects.all().order_by('-id')
    serializer_class = MotionSerializer
    fields = '__all__'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text',)


class MotionFilter(MotionView):
    queryset = Motion.objects.filter(Q(result='-')|Q(vote__tags=None)).order_by('-id')

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

class LawView(viewsets.ModelViewSet):
    queryset = Law.objects.all()
    serializer_class = LawSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('session', 'epa',)


class AllEpas(viewsets.ModelViewSet):
    queryset = Law.objects.all().distinct('epa')
    serializer_class = LawSerializer
    fields = 'epa'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('session',)

class TagsView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    fields = '__all__'
