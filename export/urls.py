from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from export.views import *


urlpatterns = [
    path('misc/votes', ExportVotesView.as_view()),
    path('misc/members', ExportParliamentMembersView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])