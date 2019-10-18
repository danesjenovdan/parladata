from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from taggit.models import Tag

from parladata.models import *



class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "created_at",
            "updated_at",
            "_name",
            "name_parser",
            "_acronym",
            "gov_id",
            "classification",
            "dissolution_date",
            "founding_date",
            "description",
            "is_coalition",
            "voters",
            "parent",
            "has_voters",
            "name",
            "acronym"
        ]
    def get_name(self, obj):
        return obj.name

    def get_acronym(self, obj):
        return obj.acronym

class SpeechSerializer(serializers.ModelSerializer):
    agenda_item_order = serializers.SerializerMethodField()
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
            "version_con",
            "speaker",
            "party",
            "session",
            "agenda_item",
            "debate",
            "agenda_items",
            "agenda_item_order"
        ]

    def get_agenda_item_order(self, obj):
        if obj.agenda_items.first():
            return obj.agenda_items.first().order
        elif obj.debate and obj.debate.order:
            return obj.debate.order
        else:
            return 0

class MotionSerializer(serializers.ModelSerializer):
    vote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Motion
        fields = '__all__'

class AgendaItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    class Meta:
        model = AgendaItem
        fields = '__all__'

class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = '__all__'

class VoteSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    results = serializers.SerializerMethodField()
    class Meta:
        model = Vote
        fields = '__all__'
    def get_results(self, obj):
        return obj.getResult()


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = '__all__'


class LinkSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    class Meta:
        model = Link
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    person = serializers.SerializerMethodField()
    class Meta:
        model = Post
        exclude = ()

    def get_person(self, obj):
        return obj.membership.person_id

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

class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetail
        fields = '__all__'


class BallotTableSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    class Meta:
        model = Ballot
        fields = (
            'id',
            'voter',
            'voterparty',
            'orgvoter',
            'result',
            'text',
            'date',
            'vote',
            'session_id',
            'tags',
            'option'
        )

    def get_result(self, obj):
        return False if obj.vote.motion.result == '0' else True

    def get_text(self, obj):
        return obj.vote.motion.text

    def get_date(self, obj):
        return obj.vote.start_time

    def get_session_id(self, obj):
        return obj.vote.session.id

    def get_tags(self, obj):
        return [tag.name for tag in obj.vote.tags.all()]
