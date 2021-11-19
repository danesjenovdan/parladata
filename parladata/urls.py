from django.conf.urls import url, include
from rest_framework import routers

from parladata.api_views import *
from parladata.views import *

router = routers.DefaultRouter()
router.register(r'people', PersonView)
router.register(r'mandates', MandateView)
router.register(r'sessions', SessionView)
router.register(r'motions', MotionView)
router.register(r'links', LinkView)
router.register(r'ballots', BallotView)
router.register(r'votes', VoteView)
router.register(r'speeches', SpeechView)
router.register(r'organizations', OrganizationView)
# router.register(r'organization-names', OrganizationNameView)
router.register(r'legislation', LegislationView)
router.register(r'tags', TagsView)
router.register(r'person-memberships', PersonMembershipView)
router.register(r'areas', AreaView)
router.register(r'agenda-items', AgendaItemView)
router.register(r'questions', QuestionView)
router.register(r'organization-memberships', OrganizationMembershipsViewSet)
router.register(r'media', MediumView)
router.register(r'media-reports', MediaReportView)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^merge-people', merge_people),
    url(r'^add-ballots', add_ballots),
]
