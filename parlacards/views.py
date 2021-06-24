from datetime import datetime
from math import ceil

from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.common import Mandate
from parladata.models.session import Session
from parladata.models.speech import Speech
from parladata.models.vote import Vote

from parlacards.serializers.cards import (
    PersonCardSerializer,
    GroupMembersCardSerializer,
    VotersCardSerializer,
    GroupsCardSerializer,
    GroupCardSerializer,
    SessionsCardSerializer,
    LegislationCardSerializer,
    PersonVocabularySizeCardSerializer,
    GroupVocabularySizeCardSerializer,
    PersonBallotCardSerializer,
    PersonQuestionCardSerializer,
    MostVotesInCommonCardSerializer,
    LeastVotesInCommonCardSerializer,
    PersonMembershipCardSerializer,
    PersonAvgSpeechesPerSessionCardSerializer,
    DeviationFromGroupCardSerializer,
    GroupDeviationFromGroupCardSerializer,
    PersonNumberOfQuestionsCardSerializer,
    PersonVoteAttendanceCardSerializer,
    RecentActivityCardSerializer,
    PersonMonthlyVoteAttendanceCardSerializer,
    GroupMonthlyVoteAttendanceCardSerializer,
    GroupNumberOfQuestionsCardSerializer,
    GroupQuestionCardSerializer,
    StyleScoresCardSerializer,
    GroupStyleScoresCardSerializer,
    NumberOfSpokenWordsCardSerializer,
    SessionLegislationCardSerializer,
    SpeechCardSerializer,
    VoteCardSerializer,
    PersonTfidfCardSerializer,
    GroupTfidfCardSerializer,
    GroupVoteAttendanceCardSerializer,
    GroupBallotCardSerializer,
    GroupMostVotesInCommonCardSerializer,
    GroupLeastVotesInCommonCardSerializer,
    PersonSpeechesCardSerializer,
    GroupSpeechesCardSerializer,
    GroupDiscordCardSerializer,
    SingleSessionCardSerializer,
    SessionVotesCardSerializer,
    LastSessionCardSerializer,
    MandateSpeechCardSerializer,
)
from parlacards.serializers.common import PersonScoreCardSerializer
from parlacards.serializers.speech import SpeechSerializer
from parlacards.serializers.session import SessionSerializer

from parlacards.solr import get_speeches_from_solr

from django.core.cache import cache


class CardView(APIView):
    """
    A view meant to be extended.
    It checks if the thing exists and
    returns 404 if it can't find it.
    """
    thing = None
    card_serializer = None

    def get_serializer_data(self, request, the_thing):
        serializer = self.card_serializer(
            the_thing,
            context={
                'date': request.card_date,
                'GET': request.GET
            }
        )
        return serializer.data

    def get(self, request, format=None):
        if not self.thing:
            raise NotImplementedError('You should define a thing to serialize.')

        if not self.card_serializer:
            raise NotImplementedError('You should define a serializer to use.')

        # if the thing with id exists return serialized data
        if the_thing := self.thing.objects.filter(id=request.card_id).first():
            return Response(self.get_serializer_data(request, the_thing))

        # otherwise return 404
        return Response(status=status.HTTP_404_NOT_FOUND)


class CachedCardView(CardView):
    @staticmethod
    def calculate_cache_key(request):
        return f'{request.path}_{request.card_id}_{request.card_date.strftime("%Y-%m-%d")}'

    def get(self, request, format=None):
        cache_key = None

        # only try cache if not explicitly disabled
        if not request.GET.get('no_cache', False):
            cache_key = self.calculate_cache_key(request)
            if cached_content := cache.get(cache_key):
                return Response(cached_content)

        # if the thing with id exists return serialized data
        if the_thing := self.thing.objects.filter(id=request.card_id).first():
            serializer_data = self.get_serializer_data(request, the_thing)
            if cache_key is not None:
                cache.set(cache_key, serializer_data)
            return Response(serializer_data)

        # otherwise return 404
        return Response(status=status.HTTP_404_NOT_FOUND)


class PersonInfo(CardView):
    """
    Show basic person info.
    """
    thing = Person
    card_serializer = PersonCardSerializer


class Voters(CardView):
    '''
    Show a list of all MPs belonging to an organization.
    '''
    thing = Organization
    card_serializer = VotersCardSerializer


class GroupInfo(CardView):
    """
    Show basic info of organization.
    """
    thing = Organization
    card_serializer = GroupCardSerializer


class GroupMembers(CardView):
    """
    Show organization members.
    """
    thing = Organization
    card_serializer = GroupMembersCardSerializer


class ParliamentaryGroups(CardView):
    '''
    List parties in an organization.
    '''
    thing = Organization
    card_serializer = GroupsCardSerializer


class GroupVoteAttendance(CardView):
    '''
    Group's attendance on votes.
    '''
    thing = Organization
    card_serializer = GroupVoteAttendanceCardSerializer


class Sessions(CardView):
    '''
    List sessions in a mandate.
    '''
    thing = Mandate
    card_serializer = SessionsCardSerializer


class Legislation(CardView):
    '''
    List legislation in a mandate.
    '''
    thing = Mandate
    card_serializer = LegislationCardSerializer


class VocabularySize(CardView):
    '''
    A person's vocabulary size.
    '''
    thing = Person
    card_serializer = PersonVocabularySizeCardSerializer


class GroupVocabularySize(CardView):
    '''
    An organization's vocabulary size.
    '''
    thing = Organization
    card_serializer = GroupVocabularySizeCardSerializer


class Ballots(CardView):
    '''
    A person's ballots.
    '''
    thing = Person
    card_serializer = PersonBallotCardSerializer


class GroupBallots(CardView):
    '''
    A person's ballots.
    '''
    thing = Organization
    card_serializer = GroupBallotCardSerializer


class Questions(CardView):
    '''
    A person's questions.
    '''
    thing = Person
    card_serializer = PersonQuestionCardSerializer


class MostVotesInCommon(CardView):
    '''
    A person's most equal voters.
    '''
    thing = Person
    card_serializer = MostVotesInCommonCardSerializer


class LeastVotesInCommon(CardView):
    '''
    A person's least equal voters.
    '''
    thing = Person
    card_serializer = LeastVotesInCommonCardSerializer


class PersonMembership(CardView):
    '''
    A person's memberships.
    '''
    thing = Person
    card_serializer = PersonMembershipCardSerializer


class PersonAvgSpeechesPerSession(CardView):
    '''
    A person's averaga number of speeches per session.
    '''
    thing = Person
    card_serializer = PersonAvgSpeechesPerSessionCardSerializer


class DeviationFromGroup(CardView):
    '''
    A person's deviation from group voting.
    '''
    thing = Person
    card_serializer = DeviationFromGroupCardSerializer


class GroupDeviationFromGroup(CardView):
    '''
    A person's deviation from group voting.
    '''
    thing = Organization
    card_serializer = GroupDeviationFromGroupCardSerializer


class PersonNumberOfQuestions(CardView):
    '''
    A person's number of questions.
    '''
    thing = Person
    card_serializer = PersonNumberOfQuestionsCardSerializer


class PersonVoteAttendance(CardView):
    '''
    A person's presence on votes.
    '''
    thing = Person
    card_serializer = PersonVoteAttendanceCardSerializer


class PersonMonthlyVoteAttendance(CardView):
    '''
    A person's monthly presence on votes.
    '''
    thing = Person
    card_serializer = PersonMonthlyVoteAttendanceCardSerializer


class RecentActivity(CardView):
    '''
    A person's recent activity.
    '''
    thing = Person
    card_serializer = RecentActivityCardSerializer


class GroupMonthlyVoteAttendance(CardView):
    '''
    A group's monthly presence on votes.
    '''
    thing = Organization
    card_serializer = GroupMonthlyVoteAttendanceCardSerializer


class GroupNumberOfQuestions(CardView):
    '''
    A group's number of questions.
    '''
    thing = Organization
    card_serializer = GroupNumberOfQuestionsCardSerializer


class GroupQuestions(CardView):
    '''
    A group's questions.
    '''
    thing = Organization
    card_serializer = GroupQuestionCardSerializer


class PersonStyleScores(CardView):
    '''
    A person's style scores.
    '''
    thing = Person
    card_serializer = StyleScoresCardSerializer


class GroupStyleScores(CardView):
    '''
    A person's style scores.
    '''
    thing = Organization
    card_serializer = GroupStyleScoresCardSerializer


class PersonNumberOfSpokenWords(CardView):
    '''
    A person's style scores.
    '''
    thing = Person
    card_serializer = NumberOfSpokenWordsCardSerializer


class SessionLegislation(CardView):
    thing = Session
    card_serializer = SessionLegislationCardSerializer


class SessionSpeeches(APIView):
    def get(self, request, format=None):
        # find the session and if no people were found return
        session = Session.objects.filter(id=request.card_id).first()
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # serialize the session
        session_serializer = SessionSerializer(
            session,
            context={'date': request.card_date}
        )

        speeches = Speech.objects.filter_valid_speeches(request.card_date).filter(
            session=session
        ).order_by(
            'order',
            'id' # fallback ordering
        )

        requested_page = request.GET.get('page', 1)
        requested_per_page = request.GET.get('per_page', 10)

        paginator = Paginator(speeches, requested_per_page)
        page = paginator.get_page(requested_page)

        # serialize speeches
        speeches_serializer = SpeechSerializer(
            page.object_list,
            many=True,
            context={'date': request.card_date}
        )
        return Response({
            'session': session_serializer.data,
            'results': speeches_serializer.data,
            'count': paginator.count,
            'pages': paginator.num_pages,
            'page': page.number,
            'per_page': paginator.per_page
        })


class SessionVotes(CardView):
    thing = Session
    card_serializer = SessionVotesCardSerializer


class SingleSpeech(CardView):
    thing = Speech
    card_serializer = SpeechCardSerializer


class SingleSession(CardView):
    thing = Session
    card_serializer = SingleSessionCardSerializer


class SingleVote(CardView):
    thing = Vote
    card_serializer = VoteCardSerializer


class PersonTfidfView(CardView):
    thing = Person
    card_serializer = PersonTfidfCardSerializer


class GroupTfidfView(CardView):
    thing = Organization
    card_serializer = GroupTfidfCardSerializer


class GroupMostVotesInCommon(CardView):
    '''
    A group's most equal voters.
    '''
    thing = Organization
    card_serializer = GroupMostVotesInCommonCardSerializer


class GroupLeastVotesInCommon(CardView):
    '''
    A group's least equal voters.
    '''
    thing = Organization
    card_serializer = GroupLeastVotesInCommonCardSerializer


class PersonSpeechesView(CardView):
    '''
    A person's speeches.
    '''
    thing = Person
    card_serializer = PersonSpeechesCardSerializer

    def get_serializer_data(self, request, the_thing):
        parent_data = super().get_serializer_data(request, the_thing)

        # the_thing is the person
        solr_params = {
            'people_ids': [the_thing.id],
            'highlight': True,
        }
        if request.GET.get('text', False):
            solr_params['text_query'] = request.GET['text']
        if request.GET.get('months', False):
            solr_params['months'] = request.GET['months'].split(',')

        try:
            requested_page = int(request.GET.get('page', 1))
        except ValueError:
            requested_page = 1
        try:
            requested_per_page = int(request.GET.get('per_page', 10))
        except ValueError:
            requested_per_page = 10

        (speeches, speech_count) = get_speeches_from_solr(
            **solr_params,
            page=requested_page,
            per_page=requested_per_page,
        )

        speech_serializer = SpeechSerializer(
            speeches,
            many=True,
            context={
                'date': request.card_date,
                'GET': request.GET
            }
        )

        return {
            **parent_data,
            'results': speech_serializer.data,
            'count': speech_count,
            'pages': ceil(max(1, speech_count) / requested_per_page),
            'page': requested_page,
            'per_page': requested_per_page,
        }


class GroupSpeechesView(CardView):
    '''
    A person's speeches.
    '''
    thing = Organization
    card_serializer = GroupSpeechesCardSerializer

    def get_serializer_data(self, request, the_thing):
        parent_data = super().get_serializer_data(request, the_thing)

        # the_thing is the group
        solr_params = {
            'group_ids': [the_thing.id],
            'highlight': True,
        }
        if request.GET.get('text', False):
            solr_params['text_query'] = request.GET['text']
        if request.GET.get('months', False):
            solr_params['months'] = request.GET['months'].split(',')
        if request.GET.get('people', False):
            solr_params['people_ids'] = request.GET['people'].split(',')

        try:
            requested_page = int(request.GET.get('page', 1))
        except ValueError:
            requested_page = 1
        try:
            requested_per_page = int(request.GET.get('per_page', 10))
        except ValueError:
            requested_per_page = 10

        (speeches, speech_count) = get_speeches_from_solr(
            **solr_params,
            page=requested_page,
            per_page=requested_per_page,
        )

        speech_serializer = SpeechSerializer(
            speeches,
            many=True,
            context={
                'date': request.card_date,
                'GET': request.GET
            }
        )

        return {
            **parent_data,
            'results': speech_serializer.data,
            'count': speech_count,
            'pages': ceil(max(1, speech_count) / requested_per_page),
            'page': requested_page,
            'per_page': requested_per_page,
        }


class GroupDiscordView(CardView):
    '''
    A group's discord score.
    '''
    thing = Organization
    card_serializer = GroupDiscordCardSerializer


class MandateSpeeches(CardView):
    '''
    Search speeches for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateSpeechCardSerializer


class LastSession(CardView):
    '''
    A group's discord score.
    '''
    thing = Organization
    card_serializer = LastSessionCardSerializer
