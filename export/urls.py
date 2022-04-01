from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from .views import *


urlpatterns = [
    path('export-votes', ExportVotesView.as_view()),
    path('export-parliament-members', ExportParliamentMembersView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])