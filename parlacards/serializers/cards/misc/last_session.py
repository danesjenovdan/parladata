from rest_framework import serializers

from parladata.models import Vote

from parlacards.models import SessionGroupAttendance

from parlacards.serializers.common import (
    CardSerializer,
    CommonOrganizationSerializer,
)
from parlacards.serializers.group_attendance import SessionGroupAttendanceSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.vote import SessionVoteSerializer

from parlacards.serializers.cards.session.tfidf import SessionTfidfCardSerializer

from parlacards.pagination import create_paginator

class MiscLastSessionCardSerializer(CardSerializer):
    def get_last_session(self, obj):
        # obj is the parent organization
        return obj.sessions.filter(
            speeches__isnull=False,
            motions__isnull=False
        ).distinct('id', 'start_time').latest('start_time')

    def get_results(self, obj):
        # obj is the parent organization
        last_session = self.get_last_session(obj)

        # tfidf
        tfidf_serializer = SessionTfidfCardSerializer(
            last_session,
            context=self.context
        )
        tfidf_results = tfidf_serializer.get_results(last_session)

        # attendance
        attendances = SessionGroupAttendance.objects.filter(
            session=last_session,
            timestamp__lte=self.context['date'],
        )
        attendance_serializer = SessionGroupAttendanceSerializer(
            attendances,
            many=True,
            context=self.context
        )

        return {
            'tfidf': tfidf_results,
            'attendance': attendance_serializer.data,
            'votes': None, # this is implemeted in to_representation for pagination
        }

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the parent organization
        last_session = self.get_last_session(instance)

        votes = Vote.objects.filter(
            motion__session=last_session
        ).order_by(
            'timestamp',
            'id' # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), votes, prefix='votes:')

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                **parent_data['results'],
                'votes': vote_serializer.data,
            },
        }

    def get_session(self, obj):
        # obj is the parent organization
        session = self.get_last_session(obj)
        serializer = SessionSerializer(
            session,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()
