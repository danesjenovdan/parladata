from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from parlacards.views import *

urlpatterns = [
    path('person/basic-information/', PersonInfo.as_view()),
    path('misc/members/', Voters.as_view()),
    path('group/basic-information/', GroupInfo.as_view()),
    path('group/members/', GroupMembers.as_view()),
    path('misc/groups/', ParliamentaryGroups.as_view()),
    path('misc/sessions/', Sessions.as_view()),
    path('misc/legislation/', Legislation.as_view()),
    path('person/vocabulary-size/', VocabularySize.as_view()),
    path('group/vocabulary-size/', GroupVocabularySize.as_view()),
    path('person/votes/', Ballots.as_view()),
    path('person/questions/', Questions.as_view()),
    path('person/memberships/', PersonMembership.as_view()),
    path('person/most-votes-in-common/', MostVotesInCommon.as_view()),
    path('person/least-votes-in-common/', LeastVotesInCommon.as_view()),
    path('person/deviation-from-group/', DeviationFromGroup.as_view()),
    path('person/average-number-of-speeches-per-session/', PersonAvgSpeechesPerSession.as_view()),
    path('person/number-of-questions/', PersonNumberOfQuestions.as_view()),
    path('person/presence-on-votes/', PersonPresenceOnVotes.as_view()),
    path('person/recent-activity/', RecentActivity.as_view()),
]
