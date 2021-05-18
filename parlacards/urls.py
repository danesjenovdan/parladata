from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from parlacards.views import *

urlpatterns = [
    path('person/', PersonInfo.as_view()),
    path('mps/', Voters.as_view()),
    path('organization/', OrganizationInfo.as_view()),
    path('organization-members/', OrganizationMembers.as_view()),
    path('parties/', ParliamentaryGroups.as_view()),
]


