import math

from importlib import import_module

from django.db.models import Avg, Max

from rest_framework import serializers

from parladata.models.person import Person


class CommonSerializer(serializers.Serializer):
    pass


class CardSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class PersonScoreSerializerField(serializers.Field):
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
        # value is going to be the person we're
        # serializing the score for
        person_to_serialize = value

        if 'date' not in self.context.keys():
            raise Exception(f'You need to provide a date in the serializer context.')

        # TODO move score serializers to separate file or use fully qualified name
        # get the score model
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, self.property_model_name)

        # get most recent score from this person
        # that is older than the date in the context
        score_object = ScoreModel.objects.filter(
            timestamp__lte=self.context['date'],
            person=person_to_serialize,
        ).order_by('-timestamp').first()

        # if something was found update the score
        if not score_object:
            return {
                'error': 'No score matches your criteria.'
            }

        score = score_object.value

        # get ids of all the people who are currently voters
        # in the same playing field (organization which we're
        # calculating values for)
        competition_ids = score_object.playing_field.query_voters(self.context['date']).values_list('id', flat=True)

        # iterate through the IDs and get their "latest" score ids
        relevant_scores_querysets = []
        for person_id in competition_ids:
            score_queryset = ScoreModel.objects.filter(
                timestamp__lte=self.context['date'],
                person__id=person_id
            ).order_by('-timestamp')[:1]

            relevant_scores_querysets.append(score_queryset)

        relevant_score_ids = ScoreModel.objects.none().union(*relevant_scores_querysets).values_list('id', flat=True)

        relevant_scores = ScoreModel.objects.filter(id__in=relevant_score_ids)

        # aggregate max and avg
        aggregations = relevant_scores.aggregate(
            Avg('value'),
            Max('value'),
        )

        average_score = aggregations['value__avg']
        maximum_score = aggregations['value__max']

        # find out who the people with maximum scores are
        winner_ids = relevant_scores.filter(
            value__gte=self.truncate_score(maximum_score)
        ).values_list('person__id', flat=True)

        maximum_people = Person.objects.filter(id__in=winner_ids)
        people_serializer = CommonPersonSerializer(
            maximum_people,
            many=True,
            context=self.context
        )

        return {
            'score': score,
            'average': average_score,
            'maximum': {
                'score': maximum_score,
                'mps': people_serializer.data
            }
        }


class PersonScoreSerializer(CardSerializer):
    def get_person(self, obj):
        serializer = CommonPersonSerializer(obj, context=self.context)
        return serializer.data

    def get_results(self, obj):
        raise NotImplementedError('You need to extend this serializer to return the results.')

    person = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()


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


class CommonPersonSerializer(CommonSerializer):
    def get_party(self, obj):
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
    party = serializers.SerializerMethodField()


class CommonOrganizationSerializer(CommonSerializer):
    name = VersionableSerializerField(property_model_name='OrganizationName')
    acronym = VersionableSerializerField(property_model_name='OrganizationAcronym')
    email = serializers.CharField()
    slug = serializers.CharField()
