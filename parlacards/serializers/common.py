import math

from importlib import import_module

from django.db.models import Avg, Max

from rest_framework import serializers

from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.common import Mandate

class VersionableSerializerField(serializers.Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)
    
    def to_representation(self, value):
        if 'date' not in self.context.keys():
            raise Exception(f'You need to provide a date in the serializer context.')

        object_to_serialize = value
        return object_to_serialize.versionable_property_on_date(
            owner=object_to_serialize,
            property_model_name=self.property_model_name,
            datetime=self.context['date'],
        )


class ScoreSerializerField(serializers.Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)
    
    @staticmethod
    def truncate_score(score):
        trunc_factor = 10 ** 5
        return math.trunc(score * trunc_factor) / trunc_factor
    
    def to_representation(self, value):
        # value is going to be the person or
        # organization we're serializing the score for
        # here we set the score_type to use later
        if isinstance(value, Person):
            score_type = 'person'
        elif isinstance(value, Organization):
            score_type = 'group'
        else:
            raise Exception(f'You should supply a person or an organization. Instead you supplied {value}.')

        if 'date' not in self.context.keys():
            raise Exception(f'You need to provide a date in the serializer context.')

        # TODO move score serializers to separate file or use fully qualified name
        # get the score model
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, self.property_model_name)

        # get most recent score from this person or organization
        # that is older than the date in the context
        score_object_kwargs = {
            'timestamp__lte': self.context['date'],
            score_type: value,
        }
        score_object = ScoreModel.objects.filter(
            **score_object_kwargs,
        ).order_by(
            '-timestamp'
        ).first()

        # if something was found update the score
        if not score_object:
            return {
                'error': 'No score matches your criteria.'
            }

        score = score_object.value

        # get ids of all the people or organizations who are
        # currently in the same playing field (organization 
        # which we're calculating values for)
        if score_type == 'person':
            competition_ids = score_object.playing_field.query_voters(self.context['date']).values_list('id', flat=True)
        else:
            # score_type == 'organization'
            competition_ids = score_object.playing_field.query_parliamentary_groups(self.context['date']).values_list('id', flat=True)

        # iterate through the IDs and get their "latest" score ids
        relevant_scores_querysets = []
        for competitor_id in competition_ids:
            score_queryset_kwargs = {
                'timestamp__lte': self.context['date'],
                f'{score_type}__id': competitor_id
            }

            score_queryset = ScoreModel.objects.filter(
                **score_queryset_kwargs
            ).order_by(
                '-timestamp'
            )[:1]

            relevant_scores_querysets.append(score_queryset)

        relevant_score_ids = ScoreModel.objects.none().union(
            *relevant_scores_querysets
        ).values(
            'id'
        )

        relevant_scores = ScoreModel.objects.filter(id__in=relevant_score_ids)

        # aggregate max and avg
        aggregations = relevant_scores.aggregate(
            Avg('value'),
            Max('value'),
        )

        average_score = aggregations['value__avg']
        maximum_score = aggregations['value__max']

        # find out who the people or organizations with maximum scores are
        winner_ids = relevant_scores.filter(
            value__gte=self.truncate_score(maximum_score)
        ).values_list(f'{score_type}__id', flat=True)

        if score_type == 'person':
            maximum_competitors = Person.objects.filter(id__in=winner_ids)
            winners_serializer = CommonPersonSerializer(
                maximum_competitors,
                many=True,
                context=self.context
            )
        else:
            # score_type == 'organization'
            maximum_competitors = Organization.objects.filter(id__in=winner_ids)
            winners_serializer = CommonOrganizationSerializer(
                maximum_competitors,
                many=True,
                context=self.context
            )

        maximum_dict_key = 'mps' if score_type == 'person' else 'groups'

        return {
            'score': score,
            'average': average_score,
            'maximum': {
                'score': maximum_score,
                maximum_dict_key: winners_serializer.data
            }
        }


class CommonSerializer(serializers.Serializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class MandateSerializer(CommonSerializer):
    description = serializers.CharField()
    beginning = serializers.DateTimeField()


class CardSerializer(serializers.Serializer):
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()

    def get_results(self, obj):
        raise NotImplementedError('You need to extend this serializer to return the results.')
    
    def get_mandate(self, obj):
        mandate = Mandate.objects.first()
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )

        return serializer.data

    results = serializers.SerializerMethodField()
    mandate = serializers.SerializerMethodField()
    # TODO
    # make the mandate dynamic
    # mandate = MandateSerializer()


class PersonScoreCardSerializer(CardSerializer):
    def get_person(self, obj):
        serializer = CommonPersonSerializer(obj, context=self.context)
        return serializer.data

    person = serializers.SerializerMethodField()


class GroupScoreCardSerializer(CardSerializer):
    def get_group(self, obj):
        serializer = CommonOrganizationSerializer(obj, context=self.context)
        return serializer.data

    group = serializers.SerializerMethodField()


class CommonPersonSerializer(CommonSerializer):
    def get_group(self, obj):
        active_parliamentary_group_membership = obj.parliamentary_group_on_date(self.context['date'])
        if not active_parliamentary_group_membership:
            return None

        serializer = CommonOrganizationSerializer(obj.parliamentary_group_on_date(self.context['date']), context=self.context)
        return serializer.data
    
    slug = serializers.CharField()
    name = VersionableSerializerField(property_model_name='PersonName')
    honorific_prefix = VersionableSerializerField(property_model_name='PersonHonorificPrefix')
    honorific_suffix = VersionableSerializerField(property_model_name='PersonHonorificSuffix')
    preferred_pronoun = VersionableSerializerField(property_model_name='PersonPreferredPronoun')
    group = serializers.SerializerMethodField()
    # TODO check if this works
    image = serializers.ImageField()


class CommonOrganizationSerializer(CommonSerializer):
    name = VersionableSerializerField(property_model_name='OrganizationName')
    acronym = VersionableSerializerField(property_model_name='OrganizationAcronym')
    slug = serializers.CharField()


class MonthlyAttendanceSerializer(serializers.Serializer):
    present = serializers.FloatField(source='value')
    no_mandate = serializers.FloatField()
    absent = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_absent(self, obj):
        return 100 - obj.value - obj.no_mandate

    def get_timestamp(self, obj):
        return obj.timestamp.date().isoformat()
