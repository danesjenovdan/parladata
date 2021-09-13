from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from taggit.models import Tag

from parladata.models import *
import json


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            'id',
            'created_at',
            'updated_at',
            'name',
            'honorific_prefix',
            'parser_names',
            'date_of_birth'
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


# class OrganizationNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrganizationName
#         fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "acronym",
            "gov_id",
            "classification",
            "parser_names",
            "dissolution_date",
            "founding_date",
            "description",
            "parent",
            "has_voters",
            "name",
            "acronym"
        ]
    def get_name(self, obj):
        return obj.name


class SpeechSerializer(TaggitSerializer, serializers.ModelSerializer):
    agenda_item_order = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    class Meta:
        model = Speech
        fields = [
            "id",
            "created_at",
            "updated_at",
            "valid_from",
            "valid_to",
            "content",
            "order",
            "start_time",
            "end_time",
            "speaker",
            "session",
            "agenda_item",
            "agenda_items",
            "agenda_item_order",
            "tags"
        ]

    def get_agenda_item_order(self, obj):
        if obj.agenda_items.first():
            return obj.agenda_items.first().order
        return 0


class AgendaItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    class Meta:
        model = AgendaItem
        fields = '__all__'


class VoteSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    results = serializers.SerializerMethodField()
    has_ballots = serializers.SerializerMethodField()
    class Meta:
        model = Vote
        fields = '__all__'

    def get_results(self, obj):
        return obj.get_option_counts()

    def get_has_ballots(self, obj):
        return bool(obj.ballots.count())

class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = '__all__'


class LinkSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    class Meta:
        model = Link
        fields = '__all__'


class MotionSerializer(serializers.ModelSerializer):
    vote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    links = LinkSerializer(many=True, read_only=True)
    class Meta:
        model = Motion
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class PersonMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonMembership
        fields = '__all__'


class LawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class EpaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = ('epa',)

    def to_representation(self, data):
        res = super(EpaSerializer, self).to_representation(data)
        return res['epa']


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = (
            'id',
            'member',
            'organization',
            'start_time',
            'end_time'
        )

class MandateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandate
        fields = '__all__'
