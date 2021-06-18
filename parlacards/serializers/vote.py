from django.db.models import Count

from collections import Counter

from rest_framework import serializers

from parladata.models.person import Person
from parladata.models.ballot import Ballot

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer, CommonPersonSerializer, CommonOrganizationSerializer

class VoteBallotSerializer(CommonSerializer):
    person = CommonPersonSerializer(source='personvoter')
    outlier = serializers.BooleanField()
    option = serializers.CharField()


class VoteGroupSerializer(CommonSerializer):
    def get_group(self, obj):
        # obj is group
        serializer = CommonOrganizationSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    max = serializers.DictField()
    votes = serializers.DictField()
    outliers = CommonPersonSerializer(many=True)
    group = serializers.SerializerMethodField()


class VoteSerializer(CommonSerializer):
    def get_gov_side(self, obj):
        # obj is the vote
        return {
            'coalition': {
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
                'outliers': []
            },
            'opposition': {
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
                'outliers': []
            }
        }

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
            'accepted': obj.motion.result == 'passed', # TODO this is possibly wrong
            'value': 51, # TODO this is faked, it's the percentage of progress bar to fill on the front
            'max_opt': 'for', # TODO this is faked
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

    def get_parties(self, obj):
        # obj is the vote
        vote_ballots = Ballot.objects.filter(
            vote=obj
        )

        groups = obj.motion.session.organization.query_parliamentary_groups(self.context['date'])

        # add data to groups
        for group in groups:
            group_ballots = vote_ballots.filter(
                # TODO this should be reworked
                # we need a special function
                # that finds all members with voting
                # rights in the playing field on a given date
                personvoter__in=group.query_members(self.context['date']),
            )
            
            annotated_group_ballots = group_ballots.values(
                'option'
            ).annotate(
                option_count=Count('option')
            ).order_by('-option_count')

            # set group max dict
            max_option_percentage = annotated_group_ballots.first()['option_count'] * 100 / sum(annotated_group_ballots.values_list('option_count', flat=True))
            max_option = annotated_group_ballots.first()['option']
            group.max = {
                'max_option_percentage': max_option_percentage,
                'max_option': max_option
            }

            # set group votes dict
            group_votes_params = {
                option_sum['option']: option_sum['option_count'] for option_sum in annotated_group_ballots
            }
            group.votes = {
                key: group_votes_params.get(key, 0) for key in ['absent', 'abstain', 'for', 'against']
            }

            # set group outliers
            group.outliers = [
                ballot.personvoter for ballot in group_ballots.exclude(option__in=['absent', max_option])
            ]
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

    gov_side = serializers.SerializerMethodField() # TODO this is faked
    abstract_visible = serializers.SerializerMethodField() # TODO this is faked
    session = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    parties = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    agenda_items = serializers.SerializerMethodField() # TODO this is faked
    documents = serializers.SerializerMethodField() # TODO this is faked
    name = serializers.CharField()
    legislation = serializers.SerializerMethodField() # TODO this is faked


class SessionVoteSerializer(CommonSerializer):
    def get_votes_abstain(self, obj):
        # obj is the vote
        return Ballot.objects.filter(
            vote=obj,
            option='abstain'
        ).count()
    
    def get_votes_absent(self, obj):
        # obj is the vote
        return Ballot.objects.filter(
            vote=obj,
            option='absent'
        ).count()
    
    def get_votes_for(self, obj):
        # obj is the vote
        return Ballot.objects.filter(
            vote=obj,
            option='for'
        ).count()
    
    def get_votes_against(self, obj):
        # obj is the vote
        return Ballot.objects.filter(
            vote=obj,
            option='against'
        ).count()
    
    def get_passed(self, obj):
        return None
    
    def get_session_id(self, obj):
        # obj is the vote
        return obj.motion.session.id

    def get_is_outlier(self, obj):
        # TODO
        return False
    
    def get_has_outliers(self, obj):
        # TODO
        return False
    
    def get_has_votes(self, obj):
        # TODO
        return True

    def get_title(self, obj):
        # TODO
        return obj.motion.title

    votes_abstain = serializers.SerializerMethodField()
    votes_absent = serializers.SerializerMethodField()
    votes_for = serializers.SerializerMethodField()
    votes_against = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    is_outlier = serializers.SerializerMethodField()
    has_outliers = serializers.SerializerMethodField()
    has_votes = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()


class SpeechVoteSerializer(CommonSerializer):
    result = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    votes = serializers.SerializerMethodField()

    def get_result(self, obj):
        # obj is the vote
        options = dict(Counter(list(obj.ballots.values_list('option', flat=True))))
        max_option = max(options, key=options.get)
        max_votes = options[max_option]
        all_votes = sum(options.values())
        max_percentage = max_votes*100/all_votes
        return {
            'is_outlier': False, # TODO this is faked
            'accepted': obj.motion.result == 'passed',
            'value': max_percentage,
            'max_opt': max_option,
        }

    def get_votes(self, obj):
        data = {
            'for': 0,
            'against': 0,
            'absent': 0,
            'abstain': 0
        }
        options = dict(Counter(list(obj.ballots.values_list('option', flat=True))))
        data.update(options)
        return data
