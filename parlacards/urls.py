from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from parlacards.views import *

urlpatterns = [
    path('person/basic-information/', PersonInfo.as_view()),
    path('misc/members/', Voters.as_view()),
    path('group/basic-information/', OrganizationInfo.as_view()),
    path('group/members/', OrganizationMembers.as_view()),
    path('misc/groups/', ParliamentaryGroups.as_view()),
    path('misc/sessions/', Sessions.as_view()),
    path('misc/legislation/', Legislation.as_view()),
    path('person/vocabulary-size/', VocabularySize.as_view()),
    path('organization/vocabulary-size/', OrganizationVocabularySize.as_view()),
    path('person/votes/', Ballots.as_view()),
    path('person/most-votes-in-common/', MostVotesInCommon.as_view()),
    path('person/least-votes-in-common/', LeastVotesInCommon.as_view()),
    path('person/deviation-from-group/', DeviationFromGroup.as_view()),
]
