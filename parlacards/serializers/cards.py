from django.db.models import Q

from rest_framework import serializers

from parladata.models.ballot import Ballot
from parladata.models.question import Question
from parladata.models.memberships import PersonMembership
from parladata.models.legislation import Law
from parlacards.models import VotingDistance

from parlacards.serializers.person import PersonSerializer
from parlacards.serializers.organization import OrganizationSerializer, MembersSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.legislation import LegislationSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer

from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreCardSerializer,
    OrganizationScoreCardSerializer,
    ScoreSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
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
