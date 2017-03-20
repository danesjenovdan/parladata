from django.conf.urls import patterns, url
from .counters import getPresence

urlpatterns = patterns('',
                       url(r'^getPresence', getPresence),
                       )
