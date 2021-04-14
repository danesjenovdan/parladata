from parladata.models import *
from parladata.serializers import *
from taggit.models import Tag
from rest_framework import (viewsets, pagination, permissions,
                            mixins, filters, generics, views)

from django.db.models import Q, Count
from django.conf import settings
from rest_framework.decorators import action
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


class PersonView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PersonSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class AgendaItemView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer


class DebateView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer


class SessionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('organization',)
    ordering_fields = ('-start_time',)


class OrganizationView(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = OrganizationsFilterSet
    filter_fields = ('classification',)
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
    queryset = Vote.objects.all().order_by("id")
    serializer_class = VoteSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('session', 'tags__name')
    ordering_fields = ('start_time',)
    search_fields = ('name', 'tags__name')


class UntaggedVoteView(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)

    # TODO fix this. This workaround for migration.
    tag_list = []
    # queryset = Vote.objects.all()#.exclude(tags__name__in=list(tag_list))

    #tags=Vote.tags.all()
    #tag_list = tags.values_list('name', flat=True)
    queryset = Vote.objects.all()#.exclude(tags__name__in=list(tag_list))

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
    filter_fields = ('vote__session', 'vote__session__organization')


class OrganizationMembershipsViewSet(viewsets.ModelViewSet):
    queryset = OrganizationMembership.objects.all().order_by('id')
    serializer_class = OrganizationMembershipSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, OAuth2Authentication)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



# Refactor classes below

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


class AllTimeMemberships(views.APIView):
    def get(self, request):
        members = Membership.objects.filter(role='voter').exclude(on_behalf_of=None)
        members = members.prefetch_related('person')
        data = []

        for member in members:
            if member.end_time != None:
                if members.filter(Q(end_time=None) |
                                Q(start_time__gte=member.start_time),
                                person_id=member.person_id).exclude(id=member.id):
                    continue
            data.append({'start_time': member.start_time,
                            'end_time': member.end_time,
                            "id": member.person.id,
                            'name': member.person.name,
                            'membership': member.on_behalf_of.name,
                            'parent_org_id': member.organization_id,
                            'acronym': member.on_behalf_of.acronym,
                            'family_name': member.person.family_name,
                            'given_name': member.person.given_name,
                            'additional_name': member.person.additional_name,
                            'honorific_prefix': member.person.honorific_prefix,
                            'honorific_suffix': member.person.honorific_suffix,
                            'patronymic_name': member.person.patronymic_name,
                            'sort_name': member.person.sort_name,
                            'email': '',
                            'gender': member.person.gender,
                            'birth_date': member.person.birth_date,
                            'death_date': member.person.death_date,
                            'summary': member.person.summary,
                            'biography': member.person.biography,
                            'image': member.person.image,
                            #     'district': districts,
                            'gov_url': member.person.gov_url.url if member.person.gov_url else '',
                            'gov_id': member.person.gov_id,
                            'gov_picture_url': member.person.gov_picture_url,
                            'voters': member.person.voters,
                            'active': member.person.active,
                            'party_id': member.on_behalf_of_id})
        return Response(data)


class AllPGsExt(views.APIView):
    def get(self, request):
        mm = Membership.objects.filter(role='voter').distinct('on_behalf_of').prefetch_related('on_behalf_of')
        data = {membership.on_behalf_of_id: {'name': membership.on_behalf_of.name,
                        'acronym': membership.on_behalf_of.acronym,
                        'id': membership.on_behalf_of_id,
                        'founded': membership.on_behalf_of.founding_date,
                        'parent_org_id': membership.organization_id,
                        'is_coalition': True if membership.on_behalf_of.is_coalition == 1 else False,
                        'disbanded': membership.on_behalf_of.dissolution_date} for membership in mm}

        return Response(data)


class AllORGsExt(views.APIView):
    def get(self, request):
        mm = Membership.objects.filter(role='voter').distinct('on_behalf_of').prefetch_related('on_behalf_of')
        data = {
            membership.on_behalf_of.id: {
                'name': membership.on_behalf_of.name,
                'id': membership.on_behalf_of.id,
                'acronym': membership.on_behalf_of.acronym,
                'founded': membership.on_behalf_of.founding_date,
                'parent_org_id': membership.organization_id,
                'type': 'party',
                'is_coalition': True if membership.on_behalf_of.is_coalition == 1 else False,
                'disbanded': membership.on_behalf_of.dissolution_date
            } for membership in mm if membership.on_behalf_of and membership.on_behalf_of.classification != 'unaligned MP'}

        parliament_sides = Organization.objects.filter(classification__in=['coalition', 'opposition'])
        for pg in parliament_sides:
            data[pg.id] = {'name': pg.name,
                        'id': pg.id,
                        'acronym': pg.acronym,
                        'founded': pg.founding_date,
                        'parent_org_id': settings.DZ_ID,
                        'type': 'coalition' if pg.is_coalition == 1 else 'opposition',
                        'is_coalition': True if pg.is_coalition == 1 else False,
                        'disbanded': pg.dissolution_date}
        parliament = Organization.objects.get(id=settings.DZ_ID)
        mm = Membership.objects.filter(role='voter').distinct('organization').prefetch_related('organization')
        for membership in mm:
            data[membership.organization_id] = {
                'name': membership.organization.name,
                'id': membership.organization.id,
                'acronym': membership.organization.acronym,
                'founded': membership.organization.founding_date,
                'type': 'parliament',
                'parent_org_id': None,
                'is_coalition': False,
                'disbanded': membership.organization.dissolution_date}
        return Response(data)


class NumberOfSpeeches(views.APIView):
    def get(self, request):
        people = {person['speaker']: person['total']
                  for person
                  in Speech.getValidSpeeches(datetime.now()).all().values('speaker').annotate(total=Count('speaker')).order_by('total')}

        orgs = {org['party']: org['total']
                for org
                in Speech.getValidSpeeches(datetime.now()).all().values('party').annotate(total=Count('party')).order_by('total')}

        all_speeches = Speech.getValidSpeeches(datetime.now()).count()

        return Response({'people': people,
                            'orgs': orgs,
                            'all_speeches': all_speeches})
