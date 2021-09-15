from itertools import chain
from importlib import import_module

from datetime import timedelta
from django.core.paginator import Paginator

from django.db.models import Q, Count, Max
from django.db.models.functions import TruncDay

from rest_framework import serializers

from parladata.models.ballot import Ballot
from parladata.models.vote import Vote
from parladata.models.question import Question
from parladata.models.memberships import PersonMembership
from parladata.models.legislation import Law
from parladata.models.question import Question
from parladata.models.speech import Speech
from parladata.models.organization import Organization
from parladata.models.person import Person

from parlacards.models import (
    SessionTfidf,
    VotingDistance,
    PersonMonthlyVoteAttendance,
    GroupMonthlyVoteAttendance,
    PersonTfidf,
    GroupTfidf,
    GroupVotingDistance,
    DeviationFromGroup,
    SessionGroupAttendance
)

from parlacards.serializers.person import PersonBasicInfoSerializer
from parlacards.serializers.organization import OrganizationBasicInfoSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.legislation import LegislationSerializer, LegislationDetailSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer, GroupVotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer
from parlacards.serializers.recent_activity import DailyActivitySerializer
from parlacards.serializers.style_scores import StyleScoresSerializer
from parlacards.serializers.speech import SpeechSerializer, HighlightSerializer, SpeechWithSessionSerializer
from parlacards.serializers.vote import VoteSerializer, SessionVoteSerializer, BareVoteSerializer
from parlacards.serializers.tfidf import TfidfSerializer
from parlacards.serializers.group_attendance import SessionGroupAttendanceSerializer
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
    SessionScoreCardSerializer,
)

from parlacards.solr import parse_search_query_params, solr_select, get_votes_from_solr, get_legislation_from_solr
from parlacards.pagination import SolrPaginator, pagination_response_data, parse_pagination_query_params

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
        if text := self.context['GET'].get('text', None):
            ballots = ballots.filter(vote__motion__text__icontains=text)

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(ballots, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize ballots
        ballot_serializer = BallotSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': ballot_serializer.data,
        }


class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        questions = Question.objects.filter(
            authors=obj,
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
    def get_results(self, obj):
        # obj is the person
        memberships = PersonMembership.valid_at(self.context['date']).filter(
            member=obj,
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
        from_datetime = self.context['date'] - timedelta(days=5)

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
            authors__in=[obj],
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
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the person
        solr_params = parse_search_query_params(self.context['GET'], people_ids=[instance.id], group_ids=None, highlight=True)
        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = SolrPaginator(solr_params, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize speeches
        speeches_serializer = SpeechWithSessionSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': speeches_serializer.data,
        }


class GroupSpeechesCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        solr_params = parse_search_query_params(self.context['GET'], group_ids=[instance.id], highlight=True)
        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = SolrPaginator(solr_params, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize speeches
        speeches_serializer = SpeechWithSessionSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': speeches_serializer.data,
        }


#
# MISC
#
class PersonAnalysesSerializer(CommonPersonSerializer):
    def calculate_cache_key(self, instance):
        return f'PersonAnalysesSerializer_{instance.id}_{instance.updated_at.isoformat()}'

    def get_person_value(self, person, property_model_name):
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, property_model_name)

        score_object = ScoreModel.objects.filter(
            person_id=person.id,
            timestamp__lte=self.context['date']
        ).order_by('-timestamp').first()

        if score_object:
            return score_object.value

        return None

    def get_working_bodies(self, person):
        memberships = PersonMembership.valid_at(self.context['date']).filter(member=person)
        organizations = Organization.objects.filter(
            id__in=memberships.values_list('organization'),
            classification__in=('committee', 'commision', 'other'), # TODO: add other classifications?
        )
        organization_serializer = CommonOrganizationSerializer(
            organizations,
            context=self.context,
            many=True,
        )
        return organization_serializer.data

    def get_results(self, person):
        return {
            'mandates': person.number_of_mandates,
            'speeches_per_session': self.get_person_value(person, 'PersonAvgSpeechesPerSession'),
            'number_of_questions': self.get_person_value(person, 'PersonNumberOfQuestions'),
            'mismatch_of_pg': self.get_person_value(person, 'DeviationFromGroup'),
            'presence_votes': self.get_person_value(person, 'PersonVoteAttendance'),
            'birth_date': person.date_of_birth.isoformat() if person.date_of_birth else None,
            'education': person.education_level,
            'spoken_words': self.get_person_value(person, 'PersonNumberOfSpokenWords'),
            'vocabulary_size': self.get_person_value(person, 'PersonVocabularySize'),
            'working_bodies': self.get_working_bodies(person),
        }

    results = serializers.SerializerMethodField()


class VotersCardSerializer(CardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the organization
        people = instance.query_voters(self.context['date']).order_by(
            'personname__value', # TODO: will this work correctly when people have multiple names?
            'id' # fallback ordering
        )

        # TODO check if sorting of analyses is optimized enough

        order_mapping = {
            'speeches_per_session': 'PersonAvgSpeechesPerSession',
            'number_of_questions': 'PersonNumberOfQuestions',
            'mismatch_of_pg': 'DeviationFromGroup',
            'presence_votes': 'PersonVoteAttendance',
            'spoken_words': 'PersonNumberOfSpokenWords',
            'vocabulary_size': 'PersonVocabularySize',
        }
        order_by = self.context['GET'].get('order_by', 'name')
        property_model_name = order_mapping.get(order_by, None)
        if order_by == 'name' or not property_model_name:
            ordered_people = people
        else:
            scores_module = import_module('parlacards.models')
            ScoreModel = getattr(scores_module, property_model_name)

            latest_scores = ScoreModel.objects.filter(
                person__in=people
            ).order_by(
                'person',
                '-timestamp'
            ).distinct(
                'person'
            ).values(
                'person',
                'value'
            )

            people_by_id = {person.id: person for person in people}

            sorted_scores = sorted(list(latest_scores), key=lambda x: x['value'], reverse=True)

            ordered_people = [people_by_id[score['person']] for score in sorted_scores]

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(ordered_people, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize people
        people_serializer = PersonAnalysesSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': people_serializer.data,
        }


class GroupAnalysesSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, instance):
        return f'GroupAnalysesSerializer_{instance.id}_{instance.updated_at.strftime("%Y-%m-%d-%H-%M-%s")}'

    def get_group_value(self, group, property_model_name):
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, property_model_name)

        score_object = ScoreModel.objects.filter(
            group_id=group.id,
            timestamp__lte=self.context['date']
        ).order_by('-timestamp').first()

        if score_object:
            return score_object.value
        return None

    def get_results(self, obj):
        return {
            'seat_count': obj.number_of_members_at(self.context['date']),
            'intra_disunion': self.get_group_value(obj, 'GroupDiscord'),
            'number_of_amendments': None, # TODO
            'vocabulary_size': self.get_group_value(obj, 'GroupVocabularySize'),
            'number_of_questions': self.get_group_value(obj, 'GroupNumberOfQuestions'),
            'vote_attendance': self.get_group_value(obj, 'GroupVoteAttendance'),
        }

    results = serializers.SerializerMethodField()


class GroupsCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the parent organization
        serializer = GroupAnalysesSerializer(
            obj.query_parliamentary_groups(self.context['date']),
            many=True,
            context=self.context
        )
        return serializer.data


class SessionsCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        serializer = SessionSerializer(
            obj.sessions.filter(
                Q(start_time__lte=self.context['date']) | Q(start_time__isnull=True)
            ),
            many=True,
            context=self.context
        )
        return serializer.data


class LegislationCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        serializer = LegislationSerializer(
            Law.objects.filter(
                Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True),
                session__mandate=obj,
            ),
            many=True,
            context=self.context
        )
        return serializer.data


class LegislationDetailCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the law
        serializer = LegislationDetailSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class LastSessionCardSerializer(CardSerializer):
    def get_last_session(self, obj):
        # obj is the parent organization
        return obj.sessions.filter(
            speeches__isnull=False,
            motions__isnull=False
        ).distinct('id', 'start_time').latest('start_time')

    def get_results(self, obj):
        # obj is the parent organization
        last_session = self.get_last_session(obj)

        # tfidf
        tfidf_serializer = SessionTfidfCardSerializer(
            last_session,
            context=self.context
        )
        tfidf_results = tfidf_serializer.get_results(last_session)

        # attendance
        attendances = SessionGroupAttendance.objects.filter(
            session=last_session,
            timestamp__lte=self.context['date'],
        )
        attendance_serializer = SessionGroupAttendanceSerializer(
            attendances,
            many=True,
            context=self.context
        )

        return {
            'tfidf': tfidf_results,
            'attendance': attendance_serializer.data,
            'votes': None, # this is implemeted in to_representation for pagination
        }

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the parent organization
        last_session = self.get_last_session(instance)

        votes = Vote.objects.filter(
            motion__session=last_session
        ).order_by(
            'timestamp',
            'id' # fallback ordering
        )

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'], prefix='votes:')
        paginator = Paginator(votes, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page, prefix='votes:'),
            'results': {
                **parent_data['results'],
                'votes': vote_serializer.data,
            },
        }

    def get_session(self, obj):
        # obj is the parent organization
        session = self.get_last_session(obj)
        serializer = SessionSerializer(
            session,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()


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

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'], prefix='members:')
        paginator = Paginator(members, requested_per_page)
        page = paginator.get_page(requested_page)

        people_serializer = CommonPersonSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page, prefix='members:'),
            'results': {
                **parent_data['results'],
                'members': people_serializer.data,
            },
        }


class GroupMembersCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

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

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(members, requested_per_page)
        page = paginator.get_page(requested_page)

        people_serializer = CommonPersonSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
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
            authors__id__in=member_ids,
        ).prefetch_related('authors')

        if not all_member_questions.exists():
            return []

        memberships = instance.query_memberships_before(timestamp)
        questions = Question.objects.none()

        for member_id in member_ids:
            member_questions = all_member_questions.filter(authors__id=member_id)

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

        # annotate all the questions
        questions = Question.objects.filter(
            id__in=questions.values('id')
        ).prefetch_related(
            'authors',
            'recipient_people',
            'links',
        ).order_by(
            '-timestamp'
        )

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(questions, requested_per_page)
        page = paginator.get_page(requested_page)

        question_serializer = QuestionSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
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
        if text := self.context['GET'].get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(votes, requested_per_page)
        page = paginator.get_page(requested_page)

        party_ballots = []
        for vote in page.object_list:
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
            **pagination_response_data(paginator, page),
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

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(speeches, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize speeches
        speeches_serializer = SpeechSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
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


class SingleSessionCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = SessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class VoteCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the vote
        serializer = VoteSerializer(
            obj,
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


class SessionTfidfCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # obj is the session
        latest_score = SessionTfidf.objects.filter(
            session=obj,
            timestamp__lte=self.context['date'],
        ).order_by(
            '-timestamp'
        ).first()

        if latest_score:
            tfidf_scores = SessionTfidf.objects.filter(
                session=obj,
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
        if text := self.context['GET'].get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        passed_string = self.context['GET'].get('passed', None)
        if passed_string in ['true', 'false']:
            passed_bool = passed_string == 'true'
            votes = votes.filter(result=passed_bool)

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = Paginator(votes, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': vote_serializer.data,
        }


#
# SPEECHES
#
class MandateSpeechCardSerializer(CardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the mandate
        solr_params = parse_search_query_params(self.context['GET'], highlight=True)
        solr_params['mandate'] = instance.description
        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])
        paginator = SolrPaginator(solr_params, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize speeches
        speeches_serializer = HighlightSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': speeches_serializer.data,
        }


class MandateUsageByGroupCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the mandate
        solr_params = parse_search_query_params(self.context['GET'], facet=True)
        solr_params['mandate'] = instance.description
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
        solr_params = parse_search_query_params(self.context['GET'], facet=True)
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
        solr_params = parse_search_query_params(self.context['GET'], facet=True)
        solr_params['mandate'] = instance.description
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


class MandateVotesCardSerializer(CardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)
        # instance is the mandate

        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])

        if text := self.context['GET'].get('text', None):
            solr_params = parse_search_query_params(self.context['GET'])
            solr_params['mandate'] = instance.description
            paginator = SolrPaginator(
                solr_params,
                requested_per_page,
                document_type='vote'
            )
        else:
            votes = Vote.objects.filter(
                timestamp__lte=self.context['date'],
                motion__session__mandate=instance
            ).order_by('-timestamp')
            paginator = Paginator(votes, requested_per_page)
    
        page = paginator.get_page(requested_page)

        # serialize votes
        vote_serializer = BareVoteSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': vote_serializer.data,
        }


class MandateLegislationCardSerializer(CardSerializer):
    def get_results(self, obj):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the mandate
        requested_page, requested_per_page = parse_pagination_query_params(self.context['GET'])

        if text := self.context['GET'].get('text', None):
            solr_params = parse_search_query_params(self.context['GET'])
            solr_params['mandate'] = instance.description
            paginator = SolrPaginator(
                solr_params,
                requested_per_page,
                document_type='law'
            )
        else:
            legislation = Law.objects.filter(
                Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True),
                session__mandate=instance,
            )

            paginator = Paginator(legislation, requested_per_page)

        page = paginator.get_page(requested_page)

        # serialize votes
        legislation_serializer = LegislationSerializer(
            page.object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_response_data(paginator, page),
            'results': legislation_serializer.data,
        }


class SearchDropdownSerializer(CardSerializer):
    def get_results(self, obj):
        # TODO THIS IS DISABLED SINCE ITS SUPER SLOW WITH LARGE NUMBER OF PEOPLE
        # REENABLE WHEN WE FIX IT
        return {
            'people': [],
            'groups': [],
        }

        # obj is the mandate

        # # TODO: get main org id more reliably
        # playing_field = Organization.objects.first()

        # # TODO: add mayor
        # people = playing_field.query_voters(self.context['date'])
        # person_serializer = CommonPersonSerializer(
        #     people,
        #     many=True,
        #     context=self.context
        # )

        # groups = playing_field.query_parliamentary_groups(self.context['date'])
        # group_serializer = CommonOrganizationSerializer(
        #     groups,
        #     many=True,
        #     context=self.context
        # )

        # return {
        #     'people': person_serializer.data,
        #     'groups': group_serializer.data,
        # }
