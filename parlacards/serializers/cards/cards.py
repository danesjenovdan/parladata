from itertools import chain
from importlib import import_module
from datetime import timedelta, datetime

from django.core.paginator import Paginator
from django.core.cache import cache

from django.db.models import Q, Count, Max
from django.db.models.functions import TruncDay

from rest_framework import serializers

from parladata.models.ballot import Ballot
from parladata.models.versionable_properties import PersonPreferredPronoun
from parladata.models.media import MediaReport
from parladata.models.vote import Vote
from parladata.models.question import Question
from parladata.models.memberships import OrganizationMembership, PersonMembership
from parladata.models.legislation import Law, LegislationClassification
from parladata.models.question import Question
from parladata.models.speech import Speech
from parladata.models.organization import Organization
from parladata.models.person import Person
from parladata.models.link import Link

from parladata.models.organization import CLASSIFICATIONS as ORGANIZATION_CLASSIFICATIONS
from parlacards.models import (
    SessionTfidf,
    VotingDistance,
    PersonMonthlyVoteAttendance,
    GroupMonthlyVoteAttendance,
    PersonTfidf,
    GroupTfidf,
    GroupVotingDistance,
    DeviationFromGroup,
    SessionGroupAttendance,
)

from parlacards.serializers.media import MediaReportSerializer
from parlacards.serializers.person import PersonBasicInfoSerializer
from parlacards.serializers.organization import OrganizationBasicInfoSerializer, RootOrganizationBasicInfoSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.legislation import LegislationSerializer, LegislationDetailSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer, GroupVotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer
from parlacards.serializers.recent_activity import DailyActivitySerializer
from parlacards.serializers.style_scores import StyleScoresSerializer
from parlacards.serializers.speech import (
    SpeechSerializer,
    HighlightSerializer,
    SpeechWithSessionSerializer,
)
from parlacards.serializers.quote import QuoteWithSessionSerializer
from parlacards.serializers.vote import VoteSerializer, SessionVoteSerializer, BareVoteSerializer
from parlacards.serializers.tfidf import TfidfSerializer
from parlacards.serializers.facets import GroupFacetSerializer, PersonFacetSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.agenda_item import AgendaItemsSerializer
from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreCardSerializer,
    GroupScoreCardSerializer,
    ScoreSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    MonthlyAttendanceSerializer,
    SessionScoreCardSerializer
)

from parlacards.solr import parse_search_query_params, solr_select
from parlacards.pagination import calculate_cache_key_for_page, create_paginator, create_solr_paginator

#
# PERSON
#
class PersonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        person_serializer = PersonBasicInfoSerializer(
            obj,
            context=self.context
        )
        return person_serializer.data


class PersonVocabularySizeCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonVocabularySize')


class PersonAvgSpeechesPerSessionCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonAvgSpeechesPerSession')


class PersonVoteAttendanceCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonVoteAttendance')


class PersonMonthlyVoteAttendanceCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        monthly_attendance = PersonMonthlyVoteAttendance.objects.filter(
            person=obj,
            timestamp__lte=self.context['date']
        ).order_by('timestamp')
        return MonthlyAttendanceSerializer(monthly_attendance, many=True).data


class PersonNumberOfQuestionsCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonNumberOfQuestions')


class GroupVocabularySizeCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupVocabularySize')


class PersonBallotCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the person
        ballots = Ballot.objects.filter(
            personvoter=instance,
            vote__timestamp__lte=self.context['date']
        ).order_by(
            '-vote__timestamp',
            '-id' # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            ballots = ballots.filter(vote__motion__text__icontains=text)

        # get options filter
        if text := self.context.get('GET', {}).get('options', None):
            options = text.split(',')
            ballots = ballots.filter(option__in=options)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), ballots)

        # serialize ballots
        ballot_serializer = BallotSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': ballot_serializer.data,
        }


class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        questions = Question.objects.filter(
            person_authors=obj,
            timestamp__lte=self.context['date']
        ).order_by(
            '-timestamp'
        ).annotate(
            date=TruncDay('timestamp')
        )

        dates_to_serialize = set(questions.values_list('date', flat=True))

        # this is ripe for optimization
        # currently iterates over all questions
        # for every date
        grouped_questions_to_serialize = [
            {
                'date': date,
                'events': questions.filter(
                    date=date
                )
            } for date in dates_to_serialize
        ]

        serializer = DailyActivitySerializer(
            grouped_questions_to_serialize,
            many=True,
            context=self.context
        )
        return serializer.data


class PersonMembershipCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # do not show memberships in root organization or parties
        filtered_classifications = [
            classification[0] for classification
            in filter(lambda x: x[0] != 'pg' and x[0] != 'root', ORGANIZATION_CLASSIFICATIONS)
        ]

        memberships = PersonMembership.valid_at(self.context['date']).filter(
            member=person,
            organization__classification__in=filtered_classifications
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
            'value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(lowest_distances)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=False)

        distances_serializer = VotingDistanceSerializer(
            sorted_distances[:5],
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
            '-value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(highest_distances)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=True)

        distances_serializer = VotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data

    results = serializers.SerializerMethodField()


class DeviationFromGroupCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='DeviationFromGroup')


class GroupDeviationFromGroupCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # TODO this is very similar to
        # ScoreSerializerField - consider refactoring
        # obj id the group
        people = obj.query_members(self.context['date'])
        deviation_scores = DeviationFromGroup.objects.filter(
            timestamp__lte=self.context['date'],
            person__in=people
        ).order_by(
            '-value'
        )

        relevant_deviation_querysets = [
            DeviationFromGroup.objects.filter(
                timestamp__lte=self.context['date'],
                person=person
            ).order_by(
                '-timestamp'
            )[:1] for person in people
        ]
        relevant_deviation_ids = DeviationFromGroup.objects.none().union(
            *relevant_deviation_querysets
        ).values(
            'id'
        )
        relevant_deviations = DeviationFromGroup.objects.filter(
            id__in=relevant_deviation_ids
        )

        return [
            {
                'person': CommonPersonSerializer(
                    deviation_score.person,
                    context=self.context
                ).data,
                'value': deviation_score.value
            } for deviation_score in relevant_deviations
        ]


class RecentActivityCardSerializer(PersonScoreCardSerializer):
    '''
    Serializes recent activity since 30 days in the past.
    '''

    def get_results(self, obj):
        # obj is the person

        # we're getting events for the past 30 days
        from_datetime = self.context['date'] - timedelta(days=30)

        ballots = Ballot.objects.filter(
            personvoter=obj,
            vote__timestamp__lte=self.context['date'],
            vote__timestamp__gte=from_datetime
        ).order_by(
            '-vote__timestamp'
        ).annotate(
            date=TruncDay('vote__timestamp')
        )

        questions = Question.objects.filter(
            person_authors=obj,
            timestamp__lte=self.context['date'],
            timestamp__gte=from_datetime
        ).order_by(
            '-timestamp'
        ).annotate(
            date=TruncDay('timestamp')
        )

        speeches = Speech.objects.filter_valid_speeches(
            self.context['date']
        ).filter(
            speaker=obj,
            start_time__lte=self.context['date'],
            start_time__gte=from_datetime
        ).order_by(
            '-start_time'
        ).annotate(
            date=TruncDay('start_time')
        )

        dates_to_serialize = set([
            *ballots.values_list('date', flat=True),
            *questions.values_list('date', flat=True),
            *speeches.values_list('date', flat=True)
        ])

        # Do NOT use chain directly if you want to iterate over it multiple
        # times. `chain` is just an iterator and will NOT reset on subsequent
        # iterations. Iteration functions will just keep calling next() on it
        # and just see an empty list.
        events_to_serialize = list(chain(ballots, questions, speeches))

        # this is ripe for optimization
        # currently iterates over all events
        # for every date
        grouped_events_to_serialize = [
            {
                'date': date,
                'events': filter(lambda event: event.date == date, events_to_serialize)
            } for date in dates_to_serialize
        ]

        serializer = DailyActivitySerializer(
            grouped_events_to_serialize,
            many=True,
            context=self.context
        )
        return serializer.data


class StyleScoresCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is person
        serializer = StyleScoresSerializer(obj, context=self.context)
        return serializer.data

class GroupStyleScoresCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is group
        serializer = StyleScoresSerializer(obj, context=self.context)
        return serializer.data

class NumberOfSpokenWordsCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonNumberOfSpokenWords')


class PersonTfidfCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is person
        latest_score = PersonTfidf.objects.filter(
            person=obj,
            timestamp__lte=self.context['date'],
        ).order_by(
            '-timestamp'
        ).first()

        if latest_score:
            tfidf_scores = PersonTfidf.objects.filter(
                person=obj,
                timestamp=latest_score.timestamp,
            )
        else:
            tfidf_scores = []

        serializer = TfidfSerializer(
            tfidf_scores,
            many=True,
            context=self.context
        )

        return serializer.data


class PersonSpeechesCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        solr_params = parse_search_query_params(self.context.get('GET', {}), people_ids=[person.id], group_ids=None, highlight=True)
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # TODO this might be better done by Solr directly
        # sort before serializing
        # first by order, then by date (in reverse order of sort preference)
        paged_object_list.sort(key=lambda speech: speech.order, reverse=True)
        paged_object_list.sort(key=lambda speech: speech.start_time, reverse=True)

        # serialize speeches
        speeches_serializer = SpeechWithSessionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class GroupSpeechesCardSerializer(GroupScoreCardSerializer):
    def get_results(self, group):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, group):
        parent_data = super().to_representation(group)

        solr_params = parse_search_query_params(self.context.get('GET', {}), group_ids=[group.id], highlight=True)
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # serialize speeches
        speeches_serializer = SpeechWithSessionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


#
# MISC
#
class SessionsCardSerializer(CardSerializer):
    # TODO it's smelly that get_results needs
    # to exist, even though we override everything
    # in to_representation
    def get_results(self, obj):
        return None

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        order = self.context.get('GET', {}).get('order_by', '-start_time')

        sessions = mandate.sessions.filter(
            Q(start_time__lte=self.context['date']) | Q(start_time__isnull=True)
        ).order_by(order)

        # check if classification is present in the GET parameter
        # classifications should be comma-separated
        # these are organization classifications
        classification_filter = self.context.get('GET', {}).get('classification', None)
        if classification_filter:
            sessions = sessions.filter(
                organizations__classification__in=classification_filter.split(',')
            )
        # show only root organization sessions by default
        else:
            sessions = sessions.filter(
                organizations__classification='root'
            )

        # check if any individual organizations are selected and filter
        # based on those
        if organizations_filter := self.context.get('GET', {}).get('organizations', None):
            try:
                organization_ids = map(lambda x: int(x), organizations_filter.split(','))
            except ValueError:
                organization_ids = []
            sessions = sessions.filter(
                organizations__id__in=organization_ids
            )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), sessions, prefix='sessions:')

        serializer = SessionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        # TODO this should probably be a serializer of its own
        # this is where we prepare all the organizations in a single
        # dictionary so the front-end card can present filters
        relevant_organizations = Organization.objects.exclude(classification__in=['pg'])
        latest_timestamp = relevant_organizations.order_by('-updated_at').first().updated_at

        organizations_cache_key = f'AllOrganizations_{latest_timestamp.strftime("%Y-%m-%d")}'

        # if there's something in the cache return it, otherwise serialize and save
        if cached_organizations := cache.get(organizations_cache_key):
            serialized_organizations = cached_organizations
        else:
            serialized_organizations = CommonOrganizationSerializer(
                relevant_organizations,
                many=True,
                context=self.context
            ).data
            cache.set(organizations_cache_key, serialized_organizations)

        return {
            **parent_data,
            **pagination_metadata,
            'results': serializer.data,
            'organizations': serialized_organizations,
        }


class LegislationCardSerializer(CardSerializer):
    # TODO it's smelly that get_results needs
    # to exist, even though we override everything
    # in to_representation
    def get_results(self, mandate):
        return None

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        text_filter = self.context.get('GET', {}).get('text', '')
        order = self.context.get('GET', {}).get('order_by', '-timestamp')

        legislation = Law.objects.filter(
            Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True),
            session__mandate=mandate,
            text__icontains=text_filter,
        ).order_by(order)

        # check if classification is present in the GET parameter
        # classifications should be comma-separated
        # TODO this code still smells
        classification_filter = self.context.get('GET', {}).get('classification', None)
        if classification_filter:
            legislation = legislation.filter(
                classification__name__in=classification_filter.split(',')
            )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), legislation, prefix='legislation:')

        serializer = LegislationSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        classifications = LegislationClassification.objects.all().distinct('name').values_list('name', flat=True)

        return {
            **parent_data,
            **pagination_metadata,
            'results': serializer.data,
            # TODO standardize this and more importantly, cache it!
            'classifications': classifications,
        }

class LegislationDetailCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the law
        serializer = LegislationDetailSerializer(
            obj,
            context=self.context
        )
        return serializer.data


#
# ORGANIZATION
#
class GroupCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        serializer = OrganizationBasicInfoSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        members = instance.query_members_by_role(
            role='member',
            timestamp=self.context['date']
        ).order_by(
            'personname__value', # TODO: will this work correctly when people have multiple names?
            'id' # fallback ordering
        )

        if not members.exists():
            # this "if" is an optimization
            # if there are no members we should
            # not have to cache.
            #
            # it also works around a bug introduced in
            # parlacards.pagination.calculate_cache_key_for_page
            # if paged_object_list is empty call to max() fails
            #
            # we still need to return a properly structured object
            paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), Question.objects.none())
            return {
                **parent_data,
                **pagination_metadata,
                'results': {
                    **parent_data['results'],
                    'members': [],
                }
            }

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), members, prefix='members:')
        page_cache_key = f'GroupCardSerializer_{calculate_cache_key_for_page(paged_object_list, pagination_metadata)}'

        # if there's something in the cache return it, otherwise serialize and save
        if cached_members := cache.get(page_cache_key):
            page_data = cached_members
        else:
            people_serializer = CommonPersonSerializer(
                paged_object_list,
                many=True,
                context=self.context
            )
            page_data = people_serializer.data
            cache.set(page_cache_key, page_data)

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                **parent_data['results'],
                'members': page_data,
            },
        }


class GroupMembersCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        members = instance.query_members(
            timestamp=self.context['date']
        ).order_by(
            'personname__value', # TODO: will this work correctly when people have multiple names?
            'id' # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), members)

        people_serializer = CommonPersonSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': people_serializer.data,
        }


class GroupMonthlyVoteAttendanceCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        monthly_attendance = GroupMonthlyVoteAttendance.objects.filter(
            group=obj,
            timestamp__lte=self.context['date']
        ).order_by('timestamp')
        return MonthlyAttendanceSerializer(monthly_attendance, many=True).data


class GroupNumberOfQuestionsCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupNumberOfQuestions')


class GroupVoteAttendanceCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupVoteAttendance')


class GroupQuestionCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        timestamp = self.context['date']
        member_ids = instance.query_members(timestamp).values_list('id', flat=True)

        all_member_questions = Question.objects.filter(
            timestamp__lte=timestamp,
            person_authors__id__in=member_ids
        ).prefetch_related('person_authors')

        if not all_member_questions.exists():
            # TODO this used to return []
            # this "if" is an optimization
            # if there are no questions the whole function
            # takes 10 times longer to execute
            # this optimization introduced a bug
            #
            # it needs to return a properly structured object
            # it's quite possible, this sort of bug was produced
            # elsewhere
            #
            # also this whole function needs more comments
            # to explain why it's doing what it's doing
            paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), Question.objects.none())
            return {
                **parent_data,
                **pagination_metadata,
                'results': []
            }

        memberships = instance.query_memberships_before(timestamp)
        questions = Question.objects.none()

        for member_id in member_ids:
            member_questions = all_member_questions.filter(person_authors__id=member_id)

            if not member_questions.exists():
                continue

            member_memberships = memberships.filter(member_id=member_id).values('start_time', 'end_time')

            q_objects = Q()
            for membership in member_memberships:
                q_params = {}
                if membership['start_time']:
                    q_params['timestamp__gte'] = membership['start_time']
                if membership['end_time']:
                    q_params['timestamp__lte'] = membership['end_time']
                q_objects.add(
                    Q(**q_params),
                    Q.OR
                )

            questions = questions.union(member_questions.filter(q_objects))

        organization_questions = Question.objects.filter(
            timestamp__lte=timestamp,
            organization_authors=instance
        )

        questions = questions.union(organization_questions)

        # annotate all the questions
        questions = Question.objects.filter(
            id__in=questions.values('id')
        ).prefetch_related(
            'person_authors',
            'organization_authors',
            'recipient_people',
            'links',
        ).order_by(
            '-timestamp'
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), questions)

        question_serializer = QuestionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': question_serializer.data,
        }


class GroupBallotCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        votes = Vote.objects.filter(
            timestamp__lte=self.context['date']
        ).order_by(
            '-timestamp',
            '-id' # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), votes)

        party_ballots = []
        for vote in paged_object_list:
            voter_ids = PersonMembership.valid_at(vote.timestamp).filter(
                # instance is the group
                on_behalf_of=instance,
                role='voter'
            ).values_list('member_id', flat=True)

            # TODO this is very similar to
            # parlacards.scores.devaition_from_group.get_group_ballot
            # consider refactoring one or both
            # the difference is that this function needs all the ballots
            ballots = Ballot.objects.filter(
                vote=vote,
                personvoter__in=voter_ids
            ).exclude(
                # TODO Filip would remove this
                # because when everyone is absent
                # this voting event will not have
                # a max option but this needs
                # consultation with product people
                option='absent'
            )

            # if there are no ballots max option will be None
            options_aggregated = ballots.values('option').aggregate(Max('option'))

            # this is a in memory only ballot object that is only constructed
            # for the serializer to use
            fake_ballot = Ballot(
                option=options_aggregated['option__max'],
                vote=vote,
            )

            # always append a ballot to party_ballots so that pagination returns
            # an expected number of objects, even if option is None
            party_ballots.append(fake_ballot)

        # serialize ballots
        ballot_serializer = BallotSerializer(
            party_ballots,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': ballot_serializer.data,
        }


class GroupMostVotesInCommonCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        highest_distances = GroupVotingDistance.objects.filter(
            group=obj,
            timestamp__lte=self.context['date']
        ).order_by(
            'target',
            '-timestamp',
            'value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(highest_distances)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=True)

        distances_serializer = GroupVotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data


class GroupLeastVotesInCommonCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        highest_distances = GroupVotingDistance.objects.filter(
            group=obj,
            timestamp__lte=self.context['date']
        ).order_by(
            'target',
            '-timestamp',
            '-value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(highest_distances)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=True)

        distances_serializer = GroupVotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data


class GroupDiscordCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupDiscord')


class RootGroupBasicInfoCardSerializer(CardSerializer):
    def get_results(self, mandate):
        root_organization, playing_field = mandate.query_root_organizations(self.context['date'])

        serializer = RootOrganizationBasicInfoSerializer(
            root_organization,
            context=self.context
        )
        return serializer.data


#
# SESSION
#
class SessionLegislationCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = LegislationSerializer(
            Law.objects.filter(
                Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True),
                session=obj,
            ),
            many=True,
            context=self.context
        )
        return serializer.data


class SessionAgendaItemCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = AgendaItemsSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class SessionSpeechesCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the session
        speeches = Speech.objects.filter_valid_speeches(self.context['date']).filter(
            session=instance
        ).order_by(
            'order',
            'id' # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), speeches)

        # serialize speeches
        speeches_serializer = SpeechSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class SpeechCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the speech
        serializer = SpeechWithSessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class QuoteCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the quote
        serializer = QuoteWithSessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class SingleSessionCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = SessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class VoteCardSerializer(CardSerializer):
    def get_results(self, vote):
        serializer = VoteSerializer(
            vote,
            context=self.context
        )
        return serializer.data


class GroupTfidfCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is group
        latest_score = GroupTfidf.objects.filter(
            group=obj,
            timestamp__lte=self.context['date'],
        ).order_by(
            '-timestamp'
        ).first()

        if latest_score:
            tfidf_scores = GroupTfidf.objects.filter(
                group=obj,
                timestamp=latest_score.timestamp,
            )
        else:
            tfidf_scores = []

        serializer = TfidfSerializer(
            tfidf_scores,
            many=True,
            context=self.context
        )

        return serializer.data


class SessionVotesCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the session
        votes = Vote.objects.filter(
            motion__session=instance
        ).order_by(
            'timestamp',
            'id' # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        passed_string = self.context.get('GET', {}).get('passed', None)
        if passed_string in ['true', 'false']:
            passed_bool = passed_string == 'true'
            votes = votes.filter(result=passed_bool)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), votes)

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': vote_serializer.data,
        }


#
# SPEECHES
#
class MandateSpeechCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id, highlight=True)
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # serialize speeches
        speeches_serializer = HighlightSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class MandateUsageByGroupCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        solr_params = parse_search_query_params(self.context.get('GET', {}), facet=True)
        solr_params['mandate'] = obj.id
        solr_response = solr_select(**solr_params, per_page=0)

        if not solr_response.get('facet_counts', {}).get('facet_fields', {}).get('party_id', []):
            return None

        facet_counts = solr_response['facet_counts']['facet_fields']['party_id']
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {'group': Organization.objects.filter(pk=group_id).first(), 'value': value}
            for (group_id, value) in facet_counts_tuples
        ]

        facet_serializer = GroupFacetSerializer(
            objects,
            many=True,
            context=self.context
        )

        return facet_serializer.data


class MandateMostUsedByPeopleCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        people_ids = obj.personmemberships.filter(role='voter').values_list('member_id', flat=True)
        solr_params = parse_search_query_params(self.context.get('GET', {}), facet=True)
        solr_params['mandate'] = obj.id
        solr_response = solr_select(**solr_params, per_page=0)

        if not solr_response.get('facet_counts', {}).get('facet_fields', {}).get('person_id', []):
            return None

        # TODO make this better
        # slice first 10 items from the list to only show top 5 people
        # 5 times (id, value) = 10
        end_slice = 0
        people_count = 0
        for person_id in solr_response['facet_counts']['facet_fields']['person_id'][::2]:
            end_slice += 2
            if int(person_id) in people_ids:
                people_count += 1
            if people_count == 5:
                break

        facet_counts = solr_response['facet_counts']['facet_fields']['person_id'][:end_slice]
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {'person': Person.objects.filter(pk=person_id).first(), 'value': value}
            for (person_id, value) in facet_counts_tuples if int(person_id) in people_ids
        ]

        facet_serializer = PersonFacetSerializer(
            objects,
            many=True,
            context=self.context
        )

        return facet_serializer.data


class MandateUsageThroughTimeCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        solr_params = parse_search_query_params(self.context.get('GET', {}), facet=True)
        solr_params['mandate'] = obj.id
        solr_response = solr_select(**solr_params, per_page=0)

        if not solr_response.get('facet_counts', {}).get('facet_ranges', {}).get('start_time', {}).get('counts', []):
            return None

        facet_counts = solr_response['facet_counts']['facet_ranges']['start_time']['counts']
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {'timestamp': timestamp, 'value': value}
            for (timestamp, value) in facet_counts_tuples
        ]

        return objects


class MandateLegislationCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        if self.context.get('GET', {}).get('text', None):
            solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id)
            paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params, document_type='law')
        else:
            legislation = Law.objects.filter(
                Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True),
                session__mandate=mandate,
            )
            paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), legislation)

        # serialize legislation
        legislation_serializer = LegislationSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': legislation_serializer.data,
        }


class SearchDropdownSerializer(CardSerializer):
    def get_results(self, mandate):
        root_organization, playing_field = mandate.query_root_organizations(self.context['date'])

        people_data = []
        groups_data = []

        text = self.context.get('GET', {}).get('text', None)

        if text and len(text) >= 2:
            leader = root_organization.query_members_by_role('leader', self.context['date']).order_by('personname__value', 'id')
            voters = playing_field.query_voters(self.context['date']).order_by('personname__value', 'id')

            # TODO: will this work correctly when people have multiple names?
            leader = leader.filter(personname__value__icontains=text)
            voters = voters.filter(personname__value__icontains=text)

            people = leader.union(voters)

            person_serializer = CommonPersonSerializer(
                people[:10],
                many=True,
                context=self.context
            )
            people_data = person_serializer.data

            groups = playing_field.query_parliamentary_groups(self.context['date'])
            # TODO: will this work correctly when groups have multiple names?
            groups = groups.filter(
                Q(organizationname__value__icontains=text) | Q(organizationacronym__value__icontains=text)
            ).order_by('organizationname__value', 'id')
            group_serializer = CommonOrganizationSerializer(
                groups[:10],
                many=True,
                context=self.context
            )
            groups_data = group_serializer.data

        return {
            'people': people_data,
            'groups': groups_data,
        }


class PersonMediaReportsCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        reports = MediaReport.objects.filter(
            medium__active=True,
            mentioned_people=person.id
        ).order_by(
            'report_date'
        )[:50]
        # TODO do this better
        # this tries to reduce loading time and shorten the card
        # by only showing the latest 50 reports

        serializer = MediaReportSerializer(
            reports,
            many=True,
            context=self.context
        )
        return serializer.data


class GroupMediaReportsCardSerializer(GroupScoreCardSerializer):
    def get_results(self, organization):
        reports = MediaReport.objects.filter(
            medium__active=True,
            mentioned_organizations=organization.id
        ).order_by(
            'report_date'
        )[:50]
        # TODO do this better
        # this tries to reduce loading time and shorten the card
        # by only showing the latest 50 reports

        serializer = MediaReportSerializer(
            reports,
            many=True,
            context=self.context
        )
        return serializer.data
