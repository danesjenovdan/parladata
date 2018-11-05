from django.conf.urls import include, url
from .tasks import runAsyncExport, get_celery_status

urlpatterns = [
	url(r'^export', runAsyncExport),
	url(r'^status/', get_celery_status),
]
