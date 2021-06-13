from itertools import chain
from operator import attrgetter
from importlib import import_module

from datetime import datetime, timedelta

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

from parlacards.models import (
    VotingDistance,
    PersonMonthlyVoteAttendance,
    GroupMonthlyVoteAttendance,
    PersonTfidf,
    GroupTfidf,
    GroupVotingDistance,
    DeviationFromGroup
)

from parlacards.serializers.person import PersonSerializer
from parlacards.serializers.organization import OrganizationSerializer, MembersSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.legislation import LegislationSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer, GroupVotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer
from parlacards.serializers.recent_activity import DailyActivitySerializer
from parlacards.serializers.style_scores import StyleScoresSerializer
from parlacards.serializers.speech import SpeechSerializer
from parlacards.serializers.vote import VoteSerializer, SessionVoteSerializer
from parlacards.serializers.tfidf import TfidfSerializer

from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreCardSerializer,
    GroupScoreCardSerializer,
    ScoreSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    MonthlyAttendanceSerializer,
)

from parlacards.solr import get_speeches_from_solr

#
# PERSON
#
class PersonCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the person
        person_serializer = PersonSerializer(
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
        # obj is the person
        ballots = Ballot.objects.filter(
            personvoter=obj,
            vote__timestamp__lte=self.context['date']
        )
        ballot_serializer = BallotSerializer(
            ballots,
            many=True,
            context=self.context
        )
        return ballot_serializer.data


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
                'events': filter(lambda question: question.date == date, questions)
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
        # TODO return this back to 30
        from_datetime = self.context['date'] - timedelta(days=60)

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

        events_to_serialize = chain(ballots, questions, speeches)

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
        # obj is the person
        solr_params = {
            'person_id': obj.id,
            'highlight': True
        }
        if self.context['GET'].get('content', False):
            solr_params['text_query'] = self.context['GET']['content']

        serializer = SpeechSerializer(
            get_speeches_from_solr(**solr_params),
            many=True,
            context=self.context
        )
        return serializer.data


class GroupSpeechesCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        solr_params = {
            'group_id': obj.id,
            'highlight': True
        }
        if self.context['GET'].get('content', False):
            solr_params['text_query'] = self.context['GET']['content']

        serializer = SpeechSerializer(
            get_speeches_from_solr(**solr_params),
            many=True,
            context=self.context
        )
        return serializer.data

#
# MISC
#
class PersonAnalysesSerializer(CommonPersonSerializer):
    results = serializers.SerializerMethodField()

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

    def get_results(self, person):
        return {
            'gender': person.preferred_pronoun,
            'mandates': person.number_of_mandates,
            'speeches_per_session': self.get_person_value(person, 'PersonAvgSpeechesPerSession'),
            'number_of_questions': self.get_person_value(person, 'PersonNumberOfQuestions'),
            'mismatch_of_pg': self.get_person_value(person, 'DeviationFromGroup'),
            'presence_votes': self.get_person_value(person, 'PersonVoteAttendance'),
            'birth_date': person.date_of_birth.isoformat() if person.date_of_birth else None,
            'education': person.education_level,
            'spoken_words': self.get_person_value(person, 'PersonNumberOfSpokenWords'),
            'vocabulary_size': self.get_person_value(person, 'PersonVocabularySize'),
        }


class VotersCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the organization
        people = obj.query_voters(self.context['date'])
        serializer = PersonAnalysesSerializer(
            people,
            many=True,
            context=self.context
        )
        return serializer.data


class GroupAnalysesSerializer(CommonOrganizationSerializer):
    results = serializers.SerializerMethodField()

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
                Q(datetime__lte=self.context['date']) | Q(datetime__isnull=True),
                session__mandate=obj,
            ),
            many=True,
            context=self.context
        )
        return serializer.data


#
# ORGANIZATION
#
class GroupCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the group
        serializer = OrganizationSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class GroupMembersCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the group
        serializer = MembersSerializer(
            obj,
            context=self.context
        )
        return serializer.data


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
        # obj is the group
        timestamp = self.context['date']
        member_ids = obj.query_members(timestamp).values_list('id', flat=True)
        memberships = obj.query_memberships_before(timestamp)

        questions = Question.objects.none()

        for member_id in member_ids:
            member_questions = Question.objects.filter(
                timestamp__lte=timestamp,
                authors__id=member_id,
            )

            member_memberships = memberships.filter(
                member__id=member_id
            ).values(
                'start_time',
                'end_time'
            )
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
                'events': filter(lambda question: question.date == date, questions)
            } for date in dates_to_serialize
        ]

        serializer = DailyActivitySerializer(
            grouped_questions_to_serialize,
            many=True,
            context=self.context
        )
        return serializer.data


class GroupBallotCardSerializer(GroupScoreCardSerializer):
    # TODO this is very similar to
    # parlacards.scores.devaition_from_group.get_group_ballot
    # consider refactoring one or both
    # the difference is that this function needs all the ballots
    def get_results(self, group):
        votes = Vote.objects.filter(timestamp__lte=self.context['date']).order_by('-timestamp')
        party_ballots = []

        for vote in votes:
            voter_ids = PersonMembership.valid_at(vote.timestamp).filter(
                on_behalf_of=group,
                role='voter'
            ).values_list('member_id', flat=True)

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

            options_aggregated = ballots.values(
                'option'
            ).annotate(
                dcount=Count('option')
            ).order_by().aggregate(Max('option'))
            # If you don't include the order_by(),
            # you may get incorrect results if the
            # default sorting is not what you expect.

            # TODO this is lazy, possibly harmless
            # but still smells -> using personal
            # ballots as party ballots
            party_ballot = ballots.first()
            if party_ballot:
                party_ballot.option = options_aggregated['option__max']
                party_ballots.append(party_ballot)

        ballot_serializer = BallotSerializer(
            party_ballots,
            many=True,
            context=self.context
        )
        return ballot_serializer.data


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
class SessionLegislationCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = LegislationSerializer(
            Law.objects.filter(
                Q(datetime__lte=self.context['date']) | Q(datetime__isnull=True),
                session=obj,
            ),
            many=True,
            context=self.context
        )
        return serializer.data

    def get_session(self, obj):
        # obj is the session
        serializer = SessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()


class SpeechCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the speech
        serializer = SpeechSerializer(
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


class SessionVotesCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the session
        votes = Vote.objects.filter(
            motion__session=obj
        )

        # serialize speeches
        serializer = SessionVoteSerializer(
            votes,
            many=True,
            context=self.context
        )
        return serializer.data

    def get_session(self, obj):
        serializer = SessionSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()
