from django.conf.urls import patterns, include, url
from .tasks import runAsyncExport

urlpatterns = patterns('',
	url(r'^export', runAsyncExport),
)
