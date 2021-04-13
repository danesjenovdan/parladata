from django.conf.urls import url, include
from django.conf import settings
from parladata.views import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ, checkSessions
from rest_framework import routers
from parladata import admin

urlpatterns = [
    url(r'^getOrganizationMembershipsOfMembers/(?P<organization_id>\d+)', getOrganizationMembershipsOfMembers),

    url(r'^getVotersByOrganizations/(?P<date_>[\w].+)', getVotersByOrganizations),
    url(r'^getVotersByOrganizations/', getVotersByOrganizations),

    url(r'^getVotesTableExtended/(?P<by_organization>\d+)/(?P<date_to>[\w].+|)', getVotesTableExtended),
    url(r'^getVotesTableExtended/(?P<by_organization>\d+)', getVotesTableExtended),
]
