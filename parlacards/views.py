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
from parladata.models.legislation import Law

from parlacards.serializers.cards import (
    PersonCardSerializer,
    GroupMembersCardSerializer,
    SearchDropdownSerializer,
    SessionSpeechesCardSerializer,
    SessionTfidfCardSerializer,
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
    SessionGroupAttendanceSerializer,
    MandateUsageByGroupCardSerializer,
    MandateMostUsedByPeopleCardSerializer,
    MandateUsageThroughTimeCardSerializer,
    MandateVotesCardSerializer,
    MandateLegislationCardSerializer,
    LegislationDetailCardSerializer,
    SessionAgendaItemCardSerializer,
)
from parlacards.serializers.speech import SpeechSerializer

from parlacards.pagination import pagination_response_data, parse_pagination_query_params

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
        cache_key = self.calculate_cache_key(request)

        # only try cache if not explicitly disabled
        if not request.GET.get('no_cache', False):
            if cached_content := cache.get(cache_key):
                return Response(cached_content)

        # if the thing with id exists return serialized data
        if the_thing := self.thing.objects.filter(id=request.card_id).first():
            serializer_data = self.get_serializer_data(request, the_thing)
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


class SessionSpeeches(CardView):
    thing = Session
    card_serializer = SessionSpeechesCardSerializer


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


class SingleLegislation(CardView):
    thing = Law
    card_serializer = LegislationDetailCardSerializer


class PersonTfidfView(CardView):
    thing = Person
    card_serializer = PersonTfidfCardSerializer


class GroupTfidfView(CardView):
    thing = Organization
    card_serializer = GroupTfidfCardSerializer


class SessionTfidfView(CardView):
    thing = Session
    card_serializer = SessionTfidfCardSerializer


class SessionAgendaItemsView(CardView):
    thing = Session
    card_serializer = SessionAgendaItemCardSerializer


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


class GroupSpeechesView(CardView):
    '''
    A person's speeches.
    '''
    thing = Organization
    card_serializer = GroupSpeechesCardSerializer


class GroupDiscordView(CardView):
    '''
    A group's discord score.
    '''
    thing = Organization
    card_serializer = GroupDiscordCardSerializer


class MandateVotes(CardView):
    '''
    Search votes for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateVotesCardSerializer


class MandateLegislation(CardView):
    '''
    Search laws for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateLegislationCardSerializer


class MandateSpeeches(CardView):
    '''
    Search speeches for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateSpeechCardSerializer


class MandateUsageByGroup(CardView):
    '''
    Search speeches for a mandate and return word usage by group.
    '''
    thing = Mandate
    card_serializer = MandateUsageByGroupCardSerializer


class MandateMostUsedByPeople(CardView):
    '''
    Search speeches for a mandate and return word usage by group.
    '''
    thing = Mandate
    card_serializer = MandateMostUsedByPeopleCardSerializer


class MandateUsageThroughTime(CardView):
    '''
    Search speeches for a mandate and return word usage by group.
    '''
    thing = Mandate
    card_serializer = MandateUsageThroughTimeCardSerializer


class LastSession(CardView):
    '''
    A group's discord score.
    '''
    thing = Organization
    card_serializer = LastSessionCardSerializer


class SearchDropdown(CardView):
    '''
    Search field dropdown autocomplete data
    '''
    thing = Mandate
    card_serializer = SearchDropdownSerializer
