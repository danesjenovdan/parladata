from django.conf.urls import url, include
from django.conf import settings
from parladata.views import *
from parladata.api_views import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ, checkSessions
from rest_framework import routers
from parladata import admin
from rest_framework import routers

from rest_framework.documentation import include_docs_urls
router = routers.DefaultRouter()
router.register(r'people', PersonView)
router.register(r'sessions', SessionView)
router.register(r'motions', MotionView)
router.register(r'links', LinkView)
router.register(r'ballots', BallotView)
router.register(r'votes', VoteView)
router.register(r'speeches', SpeechView)
router.register(r'organizations', OrganizationView)
router.register(r'legislation', LawView)
router.register(r'tags', TagsView)
router.register(r'memberships', MembershipView)
router.register(r'areas', AreaView)
router.register(r'agenda-items', AgendaItemView)
router.register(r'questions', QuestionView)
router.register(r'debates', DebateView)
router.register(r'contact_detail', ContactDetailView)
router.register(r'posts', PostView)
router.register(r'organization_memberships', OrganizationMembershipsViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]


