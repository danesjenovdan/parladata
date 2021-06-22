from collections import Counter

from django.core.cache import cache
from django.db.models import Count

from rest_framework import serializers

from parladata.models.person import Person
from parladata.models.ballot import Ballot

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import (
    CommonSerializer,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    CommonCachableSerializer
)

class VoteBallotSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the vote
        # TODO what if ballots change?
        vote_timestamp = instance.updated_at
        person_timestamp = instance.personvoter.updated_at
        timestamp = max([vote_timestamp, person_timestamp])
        return f'VoteBallotSerializer_{instance.id}_{instance.personvoter.id}_{timestamp.strftime("%Y-%m-%d-%H-%M-%s")}'

    person = CommonPersonSerializer(source='personvoter')
    outlier = serializers.BooleanField()
    option = serializers.CharField()


class VoteGroupSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is group
        # TODO what if ballots change?
        group_timestamp = instance.updated_at
        vote_timestamp = self.context['vote'].updated_at
        timestamp = max([group_timestamp, vote_timestamp])
        return f'VoteGroupSerializer_{instance.id}_{self.context["vote"].id}_{timestamp.strftime("%Y-%m-%d-%H-%M-%s")}'

    def get_group_ballots(self, group):
        vote_ballots = Ballot.objects.filter(
            vote=self.context['vote']
        )

        group_ballots = vote_ballots.filter(
            # TODO this should be reworked
            # we need a special function
            # that finds all members with voting
            # rights in the playing field on a given date
            personvoter__in=group.query_members(self.context['date']),
        )

        return group_ballots
    
    def get_annotated_group_ballots(self, group):
        annotated_group_ballots = self.get_group_ballots(group).values(
            'option'
        ).annotate(
            option_count=Count('option')
        ).order_by('-option_count')

        return annotated_group_ballots

    def get_outliers(self, obj):
        # obj is the group
        max_option = self.get_annotated_group_ballots(obj).first()['option']

        filtered_group_ballots = self.get_group_ballots(obj).exclude(option__in=['absent', max_option])
        outliers = [
            ballot.personvoter for ballot in filtered_group_ballots
        ]

        serializer = CommonPersonSerializer(
            outliers,
            many=True,
            context=self.context
        )
        return serializer.data
    
    def get_max(self, obj):
        # obj is group
        max_option_percentage = self.get_annotated_group_ballots(obj).first()['option_count'] * 100 / sum(self.get_annotated_group_ballots(obj).values_list('option_count', flat=True))
        max_option = self.get_annotated_group_ballots(obj).first()['option']
        return {
            'max_option_percentage': max_option_percentage,
            'max_option': max_option
        }
    
    def get_votes(self, obj):
        # obj is group
        group_votes_params = {
            option_sum['option']: option_sum['option_count'] for
            option_sum in self.get_annotated_group_ballots(obj)
        }
        return {
            key: group_votes_params.get(key, 0) for
            key in ['absent', 'abstain', 'for', 'against'] # TODO get this from global var
        }

    def get_group(self, obj):
        # obj is group
        serializer = CommonOrganizationSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    max = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()
    outliers = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()


class VoteSumsSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the vote
        # TODO should the vote change when ballots change?
        # maybe touch, maybe a better cache key, but this
        # one is cheap
        return f'VoteSumsSerializer_{instance.id}_{instance.updated_at.strftime("%Y-%m-%d-%H-%M-%s")}'

    # for is a reserved word FML
    def to_representation(self, instance):
        # instance is vote
        cache_key = self.calculate_cache_key(instance)
        cached_representation = cache.get(cache_key)
        if cached_representation:
            return cached_representation

        representation = instance.get_option_counts()
        cache.set(cache_key, representation)
        return representation


class VoteSerializer(CommonSerializer):
    def get_government_sides(self, obj):
        # obj is the vote
        return [
            {
                'max': {
                    'max_option': 'for',
                    'max_option_percentage': 97.67441860465115
                },
                'votes': {
                    'absent': 1.0,
                    'abstain': 0.0,
                    'for': 42.0,
                    'against': 0.0
                },
                'outliers': [],
                'group': {
                    'name': 'Coalition',
                    'acronym': None,
                    'slug': None
                }
            },
            {
                'max': {
                    'max_option': 'against',
                    'max_option_percentage': 48.93617021276596
                },
                'votes': {
                    'absent': 4.0,
                    'abstain': 18.0,
                    'for': 2.0,
                    'against': 23.0
                },
                'outliers': [],
                'group': {
                    'name': 'Opposition',
                    'acronym': None,
                    'slug': None
                }
            }
        ]

    def get_abstract_visible(self, obj):
        return False

    def get_session(self, obj):
        # obj is the vote
        serializer = SessionSerializer(
            obj.motion.session,
            context=self.context
        )
        return serializer.data
    
    def get_result(self, obj):
        # obj is the vote
        return {
            'is_outlier': False, # TODO this is faked
            'passed': obj.motion.result,
            'max_option_percentage': 51, # TODO this is faked, it's the percentage of progress bar to fill on the front
            'max_option': 'for', # TODO this is faked
        }

    def get_members(self, obj):
        # obj is the vote
        vote_ballots = Ballot.objects.filter(
            vote=obj,
        )

        for ballot in vote_ballots:
            ballot.outlier = False # TODO this is faked

        serializer = VoteBallotSerializer(
            vote_ballots,
            many=True,
            context=self.context
        )

        return serializer.data

    def get_groups(self, obj):
        # obj is the vote
        groups = obj.motion.session.organization.query_parliamentary_groups(self.context['date'])
    
        # pass the vote to the serializer
        self.context['vote'] = obj
        serializer = VoteGroupSerializer(
            groups,
            many=True,
            context=self.context
        )
        return serializer.data
    
    def get_agenda_items(self, obj):
        return None
    
    def get_documents(self, obj):
        return None
    
    def get_legislation(self, obj):
        return None
    
    def get_all_votes(self, obj):
        # obj is the vote
        serializer = VoteSumsSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    all_votes = serializers.SerializerMethodField()
    government_sides = serializers.SerializerMethodField() # TODO this is faked
    abstract_visible = serializers.SerializerMethodField() # TODO this is faked
    session = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    agenda_items = serializers.SerializerMethodField() # TODO this is faked
    documents = serializers.SerializerMethodField() # TODO this is faked
    title = serializers.CharField(source='name')
    legislation = serializers.SerializerMethodField() # TODO this is faked


class SessionVoteSerializer(CommonSerializer):
    def get_passed(self, obj):
        # obj is the vote
        return obj.result

    def get_is_outlier(self, obj):
        # TODO some day
        return False
    
    def get_has_outliers(self, obj):
        # TODO before some day
        return False
    
    def get_has_named_votes(self, obj):
        # TODO before some day
        return True

    def get_title(self, obj):
        # TODO return motion object
        # and handle it on the front-end
        return obj.motion.title
    
    def get_all_votes(self, obj):
        # obj is the vote
        serializer = VoteSumsSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    all_votes = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    is_outlier = serializers.SerializerMethodField()
    has_outliers = serializers.SerializerMethodField()
    has_named_votes = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
        

class SpeechVoteSerializer(CommonSerializer):
    result = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    title = serializers.CharField(source='name')
    votes = serializers.SerializerMethodField()

    def get_result(self, obj):
        # obj is the vote
        options = dict(Counter(list(obj.ballots.values_list('option', flat=True)))) # TODO maybe do this directly on the db
        max_option = max(options, key=options.get)
        max_votes = options[max_option]
        all_votes = sum(options.values())
        max_percentage = max_votes*100/all_votes
        return {
            'is_outlier': False, # TODO this is faked
            'passed': obj.motion.result,
            'max_option_percentage': max_percentage,
            'max_option': max_option,
        }

    def get_votes(self, obj):
        data = {
            'for': 0,
            'against': 0,
            'absent': 0,
            'abstain': 0
        }
        options = dict(Counter(list(obj.ballots.values_list('option', flat=True)))) # TODO maybe do this directly on the db
        data.update(options)
        return data
