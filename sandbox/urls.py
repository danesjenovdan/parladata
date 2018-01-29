from django.conf.urls import url
from .counters import getPresence

urlpatterns = [
	url(r'^getPresence', getPresence),
	]
