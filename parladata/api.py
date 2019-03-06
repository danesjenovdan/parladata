from parladata.models import *
from taggit.models import Tag
from rest_framework import (serializers, viewsets, pagination, permissions,
                            mixins, filters, generics)
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import detail_route, action

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from raven.contrib.django.raven_compat.models import client

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

class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
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


class LinkSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
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

class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetail
        fields = '__all__'


# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    # authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication,)
    serializer_class = PersonSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Person.objects.all()
        mps = self.request.query_params.get('mps', None)
        if mps is not None:
            MPs_ids = Membership.objects.filter(organization__classification__in=settings.PS_NP).values_list('person', flat=True)
            queryset = queryset.filter(id__in=MPs_ids)
        return queryset


# ViewSets define the view behavior.
class AgendaItemView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer


# ViewSets define the view behavior.
class DebateView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer


class SessionView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('organization', 'id')
    ordering_fields = ('-start_time',)

    @action(detail=False)
    def sessions_with_speeches(self, request):
        sessions_ids = Speech.objects.all().distinct('session').values_list('session_id', flat=True)
        sessions = Session.objects.filter(id__id=sessions_ids)

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


class LastSessionWithVoteView(SessionView):
    queryset = Session.objects.filter(organization_id=settings.DZ_ID)


class OrganizationView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    serializer_class = OrganizationSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('name_parser', '_name')

    def get_queryset(self):
        queryset = Organization.objects.all()
        classification = self.request.query_params.get('classification', None)
        if classification is not None:
            MAP = {'Party': settings.PS_NP,
                   'WB': settings.WBS,
                   'Friends': settings.FRIENDSHIP_GROUP}
            try:
                queryset = queryset.filter(classification__in=MAP[classification])
            except:
                print("asdasd")
                client.captureException()
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(OrganizationView, self).list(request, args, kwargs)
        response.data['classifications'] = settings.PS_NP + settings.WBS + settings.FRIENDSHIP_GROUP + settings.DELEGATION + settings.COUNCIL + settings.MINISTRY_GOV + settings.GOV_STAFF + ['']
        return response



class SpeechView(viewsets.ModelViewSet):
    queryset = Speech.objects.all()
    serializer_class = SpeechSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MotionView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    queryset = Motion.objects.all().order_by('-id')
    serializer_class = MotionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('session',)
    search_fields = ('text',)


class MotionFilter(MotionView):
    queryset = Motion.objects.filter(Q(result='-')|Q(result=None)|Q(vote__tags=None)).order_by('-id')


class VoteView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('session',)
    ordering_fields = ('start_time',)
    search_fields = ('name',)


class BallotView(viewsets.ModelViewSet):
    queryset = Ballot.objects.all()
    serializer_class = BallotSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LinkView(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('person', 'tags__name', 'organization')
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)


class MembershipView(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('person', 'organization')


class AreaView(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class LawView(viewsets.ModelViewSet):
    queryset = Law.objects.all().order_by('-date')
    serializer_class = LawSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('session', 'epa',)
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)


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
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)


class QuestionView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('authors',)
    ordering_fields = ('date',)

class ContactDetailView(viewsets.ModelViewSet):
    queryset = ContactDetail.objects.all()
    serializer_class = ContactDetailSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    filter_fields = ('person', 'contact_type', 'organization')
