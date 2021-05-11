from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from parlacards.views import *

router = routers.DefaultRouter()
# router.register(r'people', PersonView)
# router.register(r'sessions', SessionView)
# router.register(r'motions', MotionView)
# router.register(r'links', LinkView)
# router.register(r'ballots', BallotView)
# router.register(r'votes', VoteView)
# router.register(r'speeches', SpeechView)
# router.register(r'organizations', OrganizationView)
# router.register(r'organization-names', OrganizationNameView)
# router.register(r'legislation', LegislationView)
# router.register(r'tags', TagsView)
# router.register(r'person-memberships', PersonMembershipView)
# router.register(r'areas', AreaView)
# router.register(r'agenda-items', AgendaItemView)
# router.register(r'questions', QuestionView)
# router.register(r'debates', DebateView)
# router.register(r'organization-memberships', OrganizationMembershipsViewSet)

urlpatterns = [
    path('person/', PersonInfo.as_view()),
]


