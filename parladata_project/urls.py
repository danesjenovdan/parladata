from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^v3/', include(('parladata.urls', 'apiV3'), namespace='APIv3')),
    url(r'^v1/sandbox/', include(('sandbox.urls', 'sandobx'), namespace='sandbox')),
    url(r'^', include_docs_urls(title='Parladata v3 API', public=True)),
    url(r'^oauth/', include(('oauth2_provider.urls', 'oauth'), namespace='oauth2_provider')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
