from itertools import chain
from operator import attrgetter

from datetime import datetime, timedelta

from django.db.models import Q
from django.db.models.functions import TruncDay

from rest_framework import serializers

from parladata.models.ballot import Ballot
from parladata.models.question import Question
from parladata.models.memberships import PersonMembership
from parladata.models.legislation import Law
from parladata.models.question import Question
from parladata.models.speech import Speech
from parlacards.models import VotingDistance, PersonMonthlyPresenceOnVote

from parlacards.serializers.person import PersonSerializer
from parlacards.serializers.organization import OrganizationSerializer, MembersSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.legislation import LegislationSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer
from parlacards.serializers.recent_activity import DailyActivitySerializer

from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreCardSerializer,
    OrganizationScoreCardSerializer,
    ScoreSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    MonthlyPresenceSerializer,
)

#
# PERSON
#
class PersonCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the person
        person_serializer = PersonSerializer(
            obj,
            context=self.context
        )
        return person_serializer.data


class PersonVocabularySizeCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonVocabularySize')


class PersonAvgSpeechesPerSessionCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonAvgSpeechesPerSession')


class PersonPresenceOnVotesCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonPresenceOnVotes')


class PersonMonthlyPresenceOnVoteCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        monthly_presences = PersonMonthlyPresenceOnVote.objects.filter(
            person=obj,
            timestamp__lte=self.context['date']
        )
        return MonthlyPresenceSerializer(monthly_presences, many=True).data


class PersonNumberOfQuestionsCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonNumberOfQuestions')


class OrganizationVocabularySizeCardSerializer(OrganizationScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='OrganizationVocabularySize')


class PersonBallotCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        ballots = Ballot.objects.filter(
            personvoter=obj,
            vote__timestamp__lte=self.context['date']
        )
        ballot_serializer = BallotSerializer(ballots, many=True)
        return ballot_serializer.data


class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        questions = Question.objects.filter(
            authors=obj,
            timestamp__lte=self.context['date']
        )
        question_serializer = QuestionSerializer(questions, context=self.context, many=True)
        return question_serializer.data


class PersonMembershipCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        memberships = PersonMembership.valid_at(self.context['date']).filter(
            member=obj,
        )
        membership_serializer = MembershipSerializer(memberships, context=self.context, many=True)
        return membership_serializer.data


class MostVotesInCommonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        lowest_distances = VotingDistance.objects.filter(
            person=obj,
            timestamp__lte=self.context['date']
        ).exclude(
            target=obj
        ).order_by(
            'target',
            '-timestamp',
            'value'
        ).distinct(
            'target'
        )[:5]
        distances_serializer = VotingDistanceSerializer(
            lowest_distances,
            many=True,
            context=self.context
        )
        
        return distances_serializer.data

    results = serializers.SerializerMethodField()


class LeastVotesInCommonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        highest_distances = VotingDistance.objects.filter(
            person=obj,
            timestamp__lte=self.context['date']
        ).exclude(
            target=obj
        ).order_by(
            'target',
            '-timestamp',
            '-value'
        ).distinct(
            'target'
        )[:5]
        distances_serializer = VotingDistanceSerializer(
            highest_distances,
            many=True,
            context=self.context
        )
        
        return distances_serializer.data

    results = serializers.SerializerMethodField()


class DeviationFromGroupCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='DeviationFromGroup')


class RecentActivityCardSerializer(PersonScoreCardSerializer):
    '''
    Serializes recent activity since 30 days in the past.
    '''

    def get_results(self, obj):
        # obj is the person

        # we're getting events for the past 30 days
        from_datetime = self.context['date'] - timedelta(days=30)

        ballots = Ballot.objects.filter(
            personvoter=obj,
            vote__timestamp__lte=self.context['date'],
            vote__timestamp__gte=from_datetime
        ).order_by(
            '-vote__timestamp'
        ).annotate(
            date=TruncDay('vote__timestamp')
        )

        questions = Question.objects.filter(
            authors__in=[obj],
            timestamp__lte=self.context['date'],
            timestamp__gte=from_datetime
        ).order_by(
            '-timestamp'
        ).annotate(
            date=TruncDay('timestamp')
        )

        speeches = Speech.objects.filter_valid_speeches(
            self.context['date']
        ).filter(
            speaker=obj,
            start_time__lte=self.context['date'],
            start_time__gte=from_datetime
        ).order_by(
            '-start_time'
        ).annotate(
            date=TruncDay('start_time')
        )

        dates_to_serialize = set([
            *ballots.values_list('date', flat=True),
            *questions.values_list('date', flat=True),
            *speeches.values_list('date', flat=True)
        ])

        events_to_serialize = chain(ballots, questions, speeches)

        # this is ripe for optimization
        # currently iterates over all events
        # for every date
        grouped_events_to_serialize = [
            {
                'date': date,
                'events': filter(lambda event: event.date == date, events_to_serialize)
            } for date in dates_to_serialize
        ]

        serializer = DailyActivitySerializer(
            grouped_events_to_serialize,
            many=True,
            context=self.context
        )
        return serializer.data


#
# MISC
#
class VotersCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the organization
        people = obj.query_voters(date=self.context['date'])
        serializer = CommonPersonSerializer(
            people,
            many=True,
            context=self.context
        )
        return serializer.data


class GroupsCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the parent organization
        serializer = CommonOrganizationSerializer(
            obj.query_parliamentary_groups(date=self.context['date']),
            many=True,
            context=self.context
        )
        return serializer.data


class SessionsCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        serializer = SessionSerializer(
            obj.sessions.filter(
                Q(start_time__lte=self.context['date']) | Q(start_time__isnull=True)
            ),
            many=True,
            context=self.context
        )
        return serializer.data


class LegislationCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        serializer = LegislationSerializer(
            Law.objects.filter(
                Q(datetime__lte=self.context['date']) | Q(datetime__isnull=True),
                session__mandate=obj,
            ),
            many=True,
            context=self.context
        )
        return serializer.data


#
# ORGANIZATION
#
class OrganizationCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the organization
        serializer = OrganizationSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class OrganizationMembersCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the organization
        serializer = MembersSerializer(
            obj,
            context=self.context
        )
        return serializer.data
