from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from export.views.person import *
from export.views.misc import *


urlpatterns = [
    # misc
    path('misc/votes', ExportVotesView.as_view()),
    path('misc/members', ExportParliamentMembersView.as_view()),
    path('misc/groups', ExportParliamentGroupsView.as_view()),
    path('misc/legislation', ExportLegislationView.as_view()),

    # people
    path('person/vocabulary-size/', ExportVocabularySize.as_view()),
    path('person/votes/', ExportPersonBallots.as_view()),
    path('person/questions/', ExportPersonQuestions.as_view()),
    path('person/memberships/', ExportPersonMembership.as_view()),
    path('person/most-votes-in-common/', ExportVotingDistance.as_view()),
    path('person/least-votes-in-common/', ExportVotingDistance.as_view()),
    path('person/deviation-from-group/', ExportDeviationFromGroup.as_view()),
    path('person/average-number-of-speeches-per-session/', ExportPersonAvgSpeechesPerSession.as_view()),
    path('person/number-of-questions/', ExportPersonNumberOfQuestions.as_view()),
    path('person/vote-attendance/', ExportPersonVoteAttendance.as_view()),
    path('person/monthly-vote-attendance/', ExportPersonMonthlyVoteAttendance.as_view()),
    path('person/style-scores/', ExportPersonStyleScores.as_view()),
    path('person/number-of-spoken-words/', ExportPersonNumberOfSpokenWords.as_view()),
    path('person/tfidf/', ExportPersonTfidfView.as_view()),
    # # next two endpoints are duplicated because we need the same data on both cards
    path('person/public-questions/', ExportPersonPublicQuestionView.as_view()),
    path('person/public-answers/', ExportPersonPublicQuestionView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])
