from parladata.models import *
from taggit.models import Tag
from rest_framework import serializers, viewsets, pagination, permissions, mixins
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import detail_route

from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

# Serializers define the API representation.
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class SpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speech
        fields = '__all__'

class MotionSerializer(serializers.ModelSerializer):
    vote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Motion
        fields = '__all__'

class AgendaItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    class Meta:
        model = AgendaItem
        fields = '__all__'

class VoteSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    results = serializers.SerializerMethodField()
    class Meta:
        model = Vote
        fields = '__all__'
    def get_results(self, obj):
        return obj.getResult()


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'

class LawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class EpaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = ('epa',)
    def to_representation(self, data):
        res = super(EpaSerializer, self).to_representation(data)
        return res['epa']

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


# ViewSets define the view behavior.
class AgendaItemView(viewsets.ModelViewSet):
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer


class SessionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('organization',)
    ordering_fields = ('start_time',)



class LastSessionWithVoteView(SessionView):
    queryset = Session.objects.filter(organization_id=settings.DZ_ID)


class OrganizationView(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class SpeechView(viewsets.ModelViewSet):
    queryset = Speech.objects.all()
    serializer_class = SpeechSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MotionView(viewsets.ModelViewSet):
    queryset = Motion.objects.all().order_by('-id')
    serializer_class = MotionSerializer
    fields = '__all__'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text',)


class MotionFilter(MotionView):
    queryset = Motion.objects.filter(Q(result='-')|Q(result=None)|Q(vote__tags=None)).order_by('-id')


class VoteView(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class BallotView(viewsets.ModelViewSet):
    queryset = Ballot.objects.all()
    serializer_class = BallotSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LinkView(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class MembershipView(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer


class AreaView(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class LawView(viewsets.ModelViewSet):
    queryset = Law.objects.all().order_by('-date')
    serializer_class = LawSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('session', 'epa',)


class AllUniqueEpas(viewsets.ModelViewSet):
    end_laws = Law.objects.filter(procedure_ended=True).distinct('epa')
    end_epas = end_laws.values_list('epa', flat=True)
    queryset = Motion.objects.exclude(epa__in=end_epas).distinct('epa')
    serializer_class = EpaSerializer
    pagination.PageNumberPagination.page_size = 100
    fields = 'epa'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('session',)


class TagsView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class QuestionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('author',)
    ordering_fields = ('date',)
