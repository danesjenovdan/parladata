from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers

from parlacards.pagination import create_paginator
from parlacards.serializers.common import CardSerializer, CommonOrganizationSerializer
from parlacards.serializers.session import SessionSerializer
from parladata.models.organization import Organization
from parladata.models.session import Session


class SessionListOrganizationSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, organization):
        timestamp = organization.updated_at
        latest_session = organization.sessions.all().order_by('-updated_at').first()
        if latest_session:
            timestamp = max([timestamp, latest_session.updated_at])
        return f'SessionListOrganizationSerializer_{organization.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_session_count(self, organization):
        return organization.sessions.count()

    session_count = serializers.SerializerMethodField()


class SessionsCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None

    def _get_organizations(self, mandate):
        relevant_organizations = Organization.objects.exclude(
            Q(classification__isnull=True) | Q(classification__in=('pg', 'friendship_group', 'delegation', 'coalition')),
        )

        mandate_start, mandate_end = mandate.get_time_range_from_mandate(mandate.ending)

        relevant_organizations = relevant_organizations.filter(
            Q(founding_date__range=(mandate_start, mandate_end)) | Q(dissolution_date__range=(mandate_start, mandate_end)) | Q(dissolution_date__isnull=True)
        )

        # cache whole list of organizations
        timestamp = relevant_organizations.order_by('-updated_at').first().updated_at
        sessions = Session.objects.filter(organizations__in=relevant_organizations)
        session_count = sessions.count()
        latest_session = sessions.order_by('-updated_at').first()
        if latest_session:
            timestamp = max([timestamp, latest_session.updated_at])

        organizations_cache_key = f'SessionCardRelevantOrganizations_{session_count}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

        # if there's something in the cache return it
        if cached_organizations := cache.get(organizations_cache_key):
            return cached_organizations

        organization_serializer = SessionListOrganizationSerializer(
            relevant_organizations,
            many=True,
            context=self.context,
        )
        cache.set(organizations_cache_key, organization_serializer.data)

        return organization_serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        order = self.context.get('GET', {}).get('order_by', None) or '-start_time'

        # filter by organization classifications (show root by default)
        classification_filter = self.context.get('GET', {}).get('classification', None) or 'root'
        classifications = classification_filter.split(',')

        # check if any individual organizations are selected and filter based on those
        organizations_filter = self.context.get('GET', {}).get('organizations', '')
        organization_ids = list(filter(lambda x: x.isdigit(), organizations_filter.split(',')))

        sessions = mandate.sessions.filter(
            Q(start_time__lte=self.context['date']) | Q(start_time__isnull=True),
            organizations__classification__in=classifications,
        ).order_by(order)

        if len(organization_ids):
            sessions = sessions.filter(organizations__id__in=organization_ids)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), sessions, prefix='sessions:')

        sessions_serializer = SessionSerializer(
            paged_object_list,
            many=True,
            context=self.context,
        )

        # organizations for displaying filter tabs and dropdowns
        organizations = self._get_organizations(mandate)

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                'sessions': sessions_serializer.data,
                'organizations': organizations,
            },
        }
