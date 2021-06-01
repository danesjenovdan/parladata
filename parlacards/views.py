from datetime import datetime

from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.common import Mandate
from parladata.models.legislation import Law

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
    PersonNumberOfQuestionsCardSerializer,
    PersonVoteAttendanceCardSerializer,
    RecentActivityCardSerializer,
    PersonMonthlyVoteAttendanceCardSerializer,
    GroupMonthlyVoteAttendanceCardSerializer,
    GroupNumberOfQuestionsCardSerializer,
    GroupQuestionCardSerializer,
)

class CardView(APIView):
    """
    A view meant to be extended.
    It checks if the thing exists and
    returns 404 if it can't find it.
    """
    thing = None
    card_serializer = None

    def get(self, request, format=None):
        if not self.thing:
            raise NotImplementedError('You should define a thing to serialize.')
        
        if not self.card_serializer:
            raise NotImplementedError('You should define a serializer to use.')

        # find the person and if no people were found return
        the_thing = self.thing.objects.filter(id=request.card_id).first()
        if not the_thing:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # serialize the results and return
        serializer = self.card_serializer(
            the_thing,
            context={'date': request.card_date}
        )
        return Response(serializer.data)


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
