from django.conf.urls import include, url
from .tasks import runAsyncExport

urlpatterns = [
	url(r'^export', runAsyncExport),
]
