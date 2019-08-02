from parladata.models import *
from parladata.serializers import *
from taggit.models import Tag
from rest_framework import (viewsets, pagination, permissions,
                            mixins, filters, generics, views)

from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import detail_route, action
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend, Filter, FilterSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from raven.contrib.django.raven_compat.models import client

class MultiValueKeyFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = 'in'
        values = value.split(',')
        return super(MultiValueKeyFilter, self).filter(qs, values)


class OrganizationsFilterSet(FilterSet):
    ids = MultiValueKeyFilter(field_name='id')

    class Meta:
        model = Organization
        fields = ('ids',)


# ViewSets define the view behavior.
class PersonView(viewsets.ModelViewSet):
    # authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication,)
    serializer_class = PersonSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Person.objects.all()
        mps = self.request.query_params.get('mps', None)
        voters_of = self.request.query_params.get('voters_of', None)
        date_ = datetime.now()
        if mps is not None:
            MPs_ids = Membership.objects.filter(
                Q(start_time__date__lte=date_) |
                Q(start_time=None),
                Q(end_time__date__gte=date_) |
                Q(end_time=None),
                organization__classification__in=settings.PS_NP,
            ).values_list('person', flat=True)
            queryset = queryset.filter(id__in=MPs_ids)
        if voters_of:
            print('voters_of', voters_of)
            MPs_ids = Membership.objects.filter(
                Q(start_time__date__lte=date_) |
                Q(start_time=None),
                Q(end_time__date__gte=date_) |
                Q(end_time=None),
                organization_id=voters_of,
                role='voter'
            ).values_list('person', flat=True)
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
        sessions = Session.objects.filter(id__in=sessions_ids)

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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = OrganizationsFilterSet
    #filter_fields = ('id',)
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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('party', 'speaker', 'session')

    def list(self, request, *args, **kwargs):
        date_ = request.GET.get('date', None)
        valid = request.GET.get('valid', False)

        if date_:
            date_ = datetime.strptime(settings.API_DATE_FORMAT, date_)
        else:
            date_ = datetime.now()
        if valid:
            queryset = self.filter_queryset(Speech.getValidSpeeches(date_))
        else:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
    filter_fields = ('session', 'tags__name')
    ordering_fields = ('start_time',)
    search_fields = ('name', 'tags__name')


class UntaggedVoteView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    tags=Vote.tags.all()
    tag_list = tags.values_list('name', flat=True)
    queryset = Vote.objects.all().exclude(tags__name__in=list(tag_list))
    serializer_class = VoteSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('session',)
    ordering_fields = ('start_time',)
    search_fields = ('name', 'tags__name')


class BallotView(viewsets.ModelViewSet):
    queryset = Ballot.objects.all()
    serializer_class = BallotSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('vote', 'voter', 'vote__session')

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
    filter_fields = ('person', 'tags__name', 'organization', 'question')
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)


class MembershipView(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('person', 'organization', 'role', 'on_behalf_of')


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('membership__person', 'organization', 'role')


class AreaView(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('calssification',)


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
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('person', 'contact_type', 'organization')


class BallotTableView(viewsets.ModelViewSet):
    queryset = Ballot.objects.all().prefetch_related('vote', 'vote__motion', 'vote__tags', 'vote__session').order_by('id')
    serializer_class = BallotTableSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('vote__session',)


class BallotTable(views.APIView):
    def get(self, request, format=None):
        queryset = Ballot.objects.all().prefetch_related('vote', 'vote__motion', 'vote__tags', 'vote__session').order_by('id')
        serializer = BallotTableSerializer(queryset, many=True)
        return Response(serializer.data)


class MPSpeeches(views.APIView):
    def get(self, request, person_id, format=None):
        date_ = request.GET.get('date', None)
        if date_:
            fdate = datetime.strptime(date_, settings.API_DATE_FORMAT).date()
        else:
            fdate = datetime.now().date()
        speeches_queryset = Speech.getValidSpeeches(fdate)
        content = speeches_queryset.filter(speaker__id=person_id,
                                        start_time__lte=fdate)
        content = list(content.values_list('content', flat=True))
        return Response(content)