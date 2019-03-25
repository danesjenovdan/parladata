from django.conf.urls import url, include
from django.conf import settings
from parladata.views import *
from parladata.api import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ, checkSessions
from rest_framework import routers
from parladata import admin
from parladata.api import *

urlpatterns = [
    url(r'^getOrganizationMembershipsOfMembers/(?P<organization_id>\d+)', getOrganizationMembershipsOfMembers),

    url(r'^getVotersByOrganizations/(?P<date_>[\w].+)', getVotersByOrganizations),
    url(r'^getVotersByOrganizations/', getVotersByOrganizations),
]
