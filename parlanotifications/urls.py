from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from parlanotifications.views import KewordView

router = routers.DefaultRouter()
router.register(r'keywords', KewordView)


urlpatterns = [
    re_path(r'^', include(router.urls)),
]
