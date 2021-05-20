from rest_framework import serializers

from parladata.models.link import Link
from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.ballot import Ballot

from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreSerializer,
    ScoreSerializerField,
    VersionableSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
)
from parlacards.serializers.area import AreaSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer

from parlacards.models import PersonVocabularySize
from parlacards.models import VotingDistance


class PersonSerializer(CommonPersonSerializer):
    # TODO this will return all links they
    # should be filtered to only contain
    # social networks
    def get_social_networks(self, obj):
        links = Link.objects.filter(person=obj)
        return {link.note: link.url for link in links}

    education = VersionableSerializerField(property_model_name='PersonEducation')
    education_level = VersionableSerializerField(property_model_name='PersonEducationLevel')
    previous_occupation = VersionableSerializerField(property_model_name='PersonPreviousOccupation')
    number_of_mandates = VersionableSerializerField(property_model_name='PersonNumberOfMandates')
    date_of_birth = serializers.DateField()
    date_of_death = serializers.DateField()
    number_of_voters = VersionableSerializerField(property_model_name='PersonNumberOfVoters')
    districts = AreaSerializer(many=True)
    social_networks = serializers.SerializerMethodField()


class PersonVocabularySizeSerializer(PersonScoreSerializer):
    results = ScoreSerializerField(property_model_name='PersonVocabularySize')


class PersonBallotSerializer(PersonScoreSerializer):
    def get_results(self, obj):
        ballots = Ballot.objects.filter(
            personvoter=obj,
            vote__timestamp__lte=self.context['date']
        )
        ballot_serializer = BallotSerializer(ballots, many=True)
        return ballot_serializer.data

    results = serializers.SerializerMethodField()


class PersonMostEqualVoterSerializer(PersonScoreSerializer):
    def get_results(self, obj):
        lowest_distances = VotingDistance.objects.filter(
            timestamp__lte=self.context['date']
        ).order_by(
            'target',
            'value'
        ).distinct('target')[:5]
        distances_serializer = VotingDistanceSerializer(
            lowest_distances,
            many=True,
            context=self.context
        )
        
        return distances_serializer.data

    results = serializers.SerializerMethodField()


class PersonLeastEqualVoterSerializer(PersonScoreSerializer):
    def get_results(self, obj):
        highest_distances = VotingDistance.objects.filter(
            timestamp__lte=self.context['date']
        ).order_by(
            'target',
            '-value'
        ).distinct('target')[:5]
        distances_serializer = VotingDistanceSerializer(
            highest_distances,
            many=True,
            context=self.context
        )
        
        return distances_serializer.data

    results = serializers.SerializerMethodField()
