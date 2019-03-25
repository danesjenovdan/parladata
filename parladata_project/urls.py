from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from rest_framework.documentation import include_docs_urls

from parladata.views import index

#admin.autodiscover()

urlpatterns = [
    #url(r'^', include_docs_urls(title='Test Suite API')),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^v1/', include('parladata.urls', namespace='API')),
    url(r'^v2/', include('parladata.urls_v2', namespace='APIv2')),
    url(r'^v1/sandbox/', include('sandbox.urls')),
    url(r'^docs/', include_docs_urls(title='My API title', public=True)),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
