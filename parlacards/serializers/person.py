from datetime import datetime

from django.utils.text import slugify

from rest_framework.serializers import (
    IntegerField,
    CharField,
    DateField,
    SerializerMethodField,
    Field
)

from parladata.models.link import Link

from parlacards.serializers.common import CardSerializer
from parlacards.serializers.organization import OrganizationSerializer
from parlacards.serializers.area import AreaSerializer


class VersionableSerializerField(Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)
    
    def to_representation(self, value):
        object_to_serialize = value
        return object_to_serialize.versionable_property_on_date(
            owner=object_to_serialize,
            property_model_name=self.property_model_name,
            datetime=self.context['date'],
        )


class PersonSerializer(CardSerializer):
    def get_party(self, obj):
        active_parliamentary_group_membership = obj.parliamentary_group_on_date(self.context['date'])
        if not active_parliamentary_group_membership:
            return None

        serializer = OrganizationSerializer(obj.parliamentary_group_on_date(self.context['date']))
        return serializer.data
    
    def get_social_networks(self, obj):
        links = Link.objects.filter(person=obj)
        return {link.note: link.url for link in links}

    slug = CharField()
    name = VersionableSerializerField(property_model_name='PersonName')
    honorific_prefix = VersionableSerializerField(property_model_name='PersonHonorificPrefix')
    honorific_suffix = VersionableSerializerField(property_model_name='PersonHonorificSuffix')
    preferred_pronoun = VersionableSerializerField(property_model_name='PersonPreferredPronoun')
    education = VersionableSerializerField(property_model_name='PersonEducation')
    education_level = VersionableSerializerField(property_model_name='PersonEducationLevel')
    previous_occupation = VersionableSerializerField(property_model_name='PersonPreviousOccupation')
    number_of_mandates = VersionableSerializerField(property_model_name='PersonNumberOfMandates')
    date_of_birth = DateField()
    date_of_death = DateField()
    number_of_voters = VersionableSerializerField(property_model_name='PersonNumberOfVoters')
    districts = AreaSerializer(many=True)
    party = SerializerMethodField()
    social_networks = SerializerMethodField()
