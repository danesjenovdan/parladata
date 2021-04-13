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
router.register(r'persons', PersonView, 'person-detail') # refactor name to people
router.register(r'sessions', SessionView)
router.register(r'last_session', LastSessionWithVoteView)
router.register(r'motions', MotionView)
router.register(r'links', LinkView)
router.register(r'ballots', BallotView)
router.register(r'votes', VoteView)
router.register(r'unedited_motions', MotionFilter)
router.register(r'speechs', SpeechView)
router.register(r'organizations', OrganizationView, 'organization-detail')
router.register(r'law', LawView)
router.register(r'allActiveEpas', AllUniqueEpas)
router.register(r'tags', TagsView)
router.register(r'memberships', MembershipView)
router.register(r'areas', AreaView)
router.register(r'agenda-items', AgendaItemView)
router.register(r'questions', QuestionView)
router.register(r'debates', DebateView)
router.register(r'contact_detail', ContactDetailView)
router.register(r'untagged_votes', UntaggedVoteView)
router.register(r'posts', PostView)
router.register(r'ballot_table', BallotTableView)
router.register(r'organization_memberships', OrganizationMembershipsViewSet)

urlpatterns = [
    # DRF APIViews
    url(r'^speeches-of-mp/(?P<person_id>\d+)/', MPSpeeches.as_view()),
    url(r'^getAllTimeMemberships/', AllTimeMemberships.as_view()), # refactor name
    url(r'^getAllPGsExt/', AllPGsExt.as_view()), # refactor name
    url(r'^getAllORGsExt/', AllORGsExt.as_view()), # refactor name
    url(r'^getNumberOfSpeeches/', NumberOfSpeeches.as_view()), # refactor name
]


