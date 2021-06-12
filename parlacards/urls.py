from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from parlacards.views import *

urlpatterns = [
    path('misc/members/', Voters.as_view()),
    path('misc/groups/', ParliamentaryGroups.as_view()),
    path('misc/sessions/', Sessions.as_view()),
    path('misc/legislation/', Legislation.as_view()),

    path('person/basic-information/', PersonInfo.as_view()),
    path('person/vocabulary-size/', VocabularySize.as_view()),
    path('person/votes/', Ballots.as_view()),
    path('person/questions/', Questions.as_view()),
    path('person/memberships/', PersonMembership.as_view()),
    path('person/most-votes-in-common/', MostVotesInCommon.as_view()),
    path('person/least-votes-in-common/', LeastVotesInCommon.as_view()),
    path('person/deviation-from-group/', DeviationFromGroup.as_view()),
    path('person/average-number-of-speeches-per-session/', PersonAvgSpeechesPerSession.as_view()),
    path('person/number-of-questions/', PersonNumberOfQuestions.as_view()),
    path('person/vote-attendance/', PersonVoteAttendance.as_view()),
    path('person/recent-activity/', RecentActivity.as_view()),
    path('person/monthly-vote-attendance/', PersonMonthlyVoteAttendance.as_view()),
    path('person/style-scores/', PersonStyleScores.as_view()),
    path('person/number-of-spoken-words/', PersonNumberOfSpokenWords.as_view()),
    path('person/tfidf/', PersonTfidfView.as_view()),

    path('group/basic-information/', GroupInfo.as_view()),
    path('group/members/', GroupMembers.as_view()),
    path('group/vocabulary-size/', GroupVocabularySize.as_view()),
    path('group/number-of-questions/', GroupNumberOfQuestions.as_view()),
    path('group/monthly-vote-attendance/', GroupMonthlyVoteAttendance.as_view()),
    path('group/questions/', GroupQuestions.as_view()),
    path('group/vote-attendance/', GroupVoteAttendance.as_view()),
    path('group/votes/', GroupBallots.as_view()),
    path('group/most-votes-in-common/', GroupMostVotesInCommon.as_view()),
    path('group/least-votes-in-common/', GroupLeastVotesInCommon.as_view()),
    path('group/deviation-from-group/', GroupDeviationFromGroup.as_view()),

    path('session/legislation/', SessionLegislation.as_view()),
    path('session/speeches/', SessionSpeeches.as_view()),

    path('speech/single/', SingleSpeech.as_view()),

    path('vote/single/', SingleVote.as_view()),
]
