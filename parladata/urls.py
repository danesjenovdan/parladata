from django.conf.urls import url, include
from rest_framework import routers

from parladata.api_views import *

router = routers.DefaultRouter()
router.register(r'people', PersonView)
router.register(r'sessions', SessionView)
router.register(r'motions', MotionView)
router.register(r'links', LinkView)
router.register(r'ballots', BallotView)
router.register(r'votes', VoteView)
router.register(r'speeches', SpeechView)
router.register(r'organizations', OrganizationView)
router.register(r'legislation', LegislationView)
router.register(r'tags', TagsView)
router.register(r'memberships', MembershipView)
router.register(r'areas', AreaView)
router.register(r'agenda-items', AgendaItemView)
router.register(r'questions', QuestionView)
router.register(r'debates', DebateView)
router.register(r'contact-detail', ContactDetailView)
router.register(r'posts', PostView)
router.register(r'organization-memberships', OrganizationMembershipsViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]


