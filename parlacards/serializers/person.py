from rest_framework import serializers

from parladata.models.link import Link
from parladata.models.person import Person
from parladata.models.organization import Organization

from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreSerializer,
    ScoreSerializerField,
    VersionableSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
)
from parlacards.serializers.area import AreaSerializer

from parlacards.models import PersonVocabularySize


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
