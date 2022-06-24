from parladata.models import *
from parladata.serializers import *
from parladata.models.versionable_properties import OrganizationName, OrganizationAcronym, PersonName, PersonPreferredPronoun
from taggit.models import Tag
from rest_framework import (viewsets, pagination, permissions,
                            mixins, filters, generics, views)

from django.db.models import Q, Count
from django.conf import settings
from rest_framework.decorators import action
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend, Filter, FilterSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, parsers
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from raven.contrib.django.raven_compat.models import client

import logging
logger = logging.getLogger('logger')


# Filters

class MultiValueKeyFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = 'in'
        values = value.split(',')
        return super(MultiValueKeyFilter, self).filter(qs, values)


class ValidSpeechesFilter(filters.BaseFilterBackend):
    """
    Filter that return valid speeches on date.
    """
    def filter_queryset(self, request, queryset, view):
        if 'valid_on' in request.GET.keys():
            valid_on = datetime.strptime(request.GET.get('valid_on'), "%Y-%m-%d")
            queryset = queryset.getValidSpeeches(valid_on)
        return queryset


class UneditedMotionsFilter(filters.BaseFilterBackend):
    """
    Filter that return unedited motions.
    """
    def filter_queryset(self, request, queryset, view):
        if request.GET.get('filter', '') == 'unedited':
            queryset = queryset.filter(Q(result='-')|Q(result=None)|Q(vote__tags=None)).order_by('-id')
        return queryset


class UntaggedVotesFilter(filters.BaseFilterBackend):
    """
    Filter that return untagged votes.
    """
    def filter_queryset(self, request, queryset, view):
        if request.GET.get('filter', '') == 'untagged':
            tag_list=Vote.tags.all().order_by('id').values_list('name', flat=True)
            queryset = queryset.exclude(tags__name__in=list(tag_list))
        return queryset


class OrganizationsFilterSet(FilterSet):
    classifications = MultiValueKeyFilter(field_name='classification')
    class Meta:
        model = Organization
        fields = ('classifications',)

## Viewsets



class CountViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def count(self, request, pk=None):
        count = self.filter_queryset(self.get_queryset()).count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class PersonView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Person.objects.all().order_by('id')
    serializer_class = PersonSerializer

    def create(self, request, *args, **kwargs):
        logging.warning(request.data)
        name = request.data.pop('name', '')
        preferred_pronoun = request.data.pop('preferred_pronoun', '')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        instance = serializer.instance
        PersonName(
            value=name,
            owner=instance
        ).save()
        PersonPreferredPronoun(
            value=preferred_pronoun,
            owner=instance
        ).save()

        headers = self.get_success_headers(serializer.data)

        data = self.get_serializer(instance).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def add_parser_name(self, request, pk=None):
        person = get_object_or_404(Person, pk=pk)
        parser_name = request.data.get('parser_name')
        person.add_parser_name(parser_name)
        person.save()

        data = self.get_serializer(person).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def upload_image(self, request, pk=None):
        person = get_object_or_404(Person, pk=pk)
        person.image = request.data.get('image')
        person.save()

        data = self.get_serializer(person).data
        return Response(data, status=status.HTTP_200_OK)


class AgendaItemView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = AgendaItem.objects.all().order_by('id')
    serializer_class = AgendaItemSerializer


class SessionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Session.objects.all().order_by('id')
    serializer_class = SessionSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ('organizations', 'mandate')
    ordering_fields = ('-start_time',)

    @action(detail=True, methods=['post'])
    def unvalidate_speeches(self, request, pk=None):
        session = get_object_or_404(Session, pk=pk)
        session.speeches.all().update(valid_to=datetime.now())
        return Response({}, status=status.HTTP_200_OK)


# class OrganizationNameView(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#     serializer_class = OrganizationNameSerializer
#     queryset = OrganizationName.objects.all().order_by('id')
#     filter_backends = (DjangoFilterBackend,)
#     filterset_fields = ('organization',)


class OrganizationView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('id')
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = OrganizationsFilterSet
    search_fields = ('name_parser', '_name')

    def create(self, request, *args, **kwargs):
        logging.warning(request.data)
        name = request.data.pop('name', '')
        acronym = request.data.pop('acronym', '')
        #parser_names = request.data.get('parser_names', '')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        instance = serializer.instance
        OrganizationName(
            value=name,
            owner=instance
        ).save()
        OrganizationAcronym(
            value=acronym,
            owner=instance
        ).save()

        headers = self.get_success_headers(serializer.data)

        data = self.get_serializer(instance).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SpeechView(CountViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Speech.objects.all().order_by('id')
    serializer_class = SpeechSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, ValidSpeechesFilter)
    filterset_fields = ('speaker', 'session', 'session__mandate')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MotionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Motion.objects.all().order_by('-id')
    serializer_class = MotionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, UneditedMotionsFilter)
    filterset_fields = ('session', 'session__mandate')
    search_fields = ('text',)


class VoteView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Vote.objects.all().order_by("id")
    serializer_class = VoteSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, UntaggedVotesFilter)
    filterset_fields = ('tags__name',)
    ordering_fields = ('start_time',)
    search_fields = ('name', 'tags__name',)


class BallotView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ballot.objects.all().order_by('id')
    serializer_class = BallotSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('vote', 'personvoter')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LinkView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Link.objects.all().order_by('id')
    serializer_class = LinkSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('person', 'tags__name', 'organization', 'question')


class DocumentView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Document.objects.all().order_by('id')
    serializer_class = DocumentSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__name',)


class PersonMembershipView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = PersonMembership.objects.all().order_by('id')
    serializer_class = PersonMembershipSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('member', 'organization', 'role', 'on_behalf_of')


class AreaView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Area.objects.all().order_by('id')
    serializer_class = AreaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('classification',)


class LegislationView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Law.objects.all().order_by('-id')
    serializer_class = LawSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('session', 'epa',)


# TODO rewrite this so it works
# class AllUniqueEpas(viewsets.ModelViewSet):
#     end_laws = Law.objects.filter(procedure_ended=True).distinct('epa')
#     end_epas = end_laws.values_list('epa', flat=True)
#     queryset = Motion.objects.exclude(epa__in=end_epas).distinct('epa').order_by('id')
#     serializer_class = EpaSerializer
#     pagination.PageNumberPagination.page_size = 100
#     fields = 'epa'
#     filter_backends = (DjangoFilterBackend,)
#     filterset_fields = ('session',)


class TagsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagsSerializer


class QuestionView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Question.objects.all().order_by('id')
    serializer_class = QuestionSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ('person_authors',)
    ordering_fields = ('date',)


class OrganizationMembershipsViewSet(viewsets.ModelViewSet):
    queryset = OrganizationMembership.objects.all().order_by('id')
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MandateView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Mandate.objects.all().order_by('-id')
    serializer_class = MandateSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('description',)


class ProcedureViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Procedure.objects.all().order_by('id')
    serializer_class = ProcedureSerializer


class ProcedurePhaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ProcedurePhase.objects.all()
    serializer_class = ProcedurePhaseSerializer


class LegislationConsiderationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = LegislationConsideration.objects.all().order_by('id')
    serializer_class = LegislationConsiderationSerializer


class LegislationStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = LegislationStatus.objects.all().order_by('id')
    serializer_class = LegislationStatusSerializer


class LegislationClassificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = LegislationClassification.objects.all().order_by('id')
    serializer_class = LegislationClassificationSerializer


class MediumView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Medium.objects.all().order_by('id')
    serializer_class = MediumSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'url', 'active')


class MediaReportView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = MediaReport.objects.all().order_by('id')
    serializer_class = MediaReportSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ('medium', 'mentioned_people', 'mentioned_organizations', 'mentioned_legislation', 'mentioned_motions', 'mentioned_votes')
    ordering_fields = ('report_date', 'retrieval_date')
