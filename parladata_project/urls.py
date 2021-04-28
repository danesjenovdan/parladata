from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v3/', include(('parladata.urls', 'apiV3'), namespace='APIv3')),
    path('v1/sandbox/', include(('sandbox.urls', 'sandobx'), namespace='sandbox')),
    path('v3/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('oauth/', include(('oauth2_provider.urls', 'oauth'), namespace='oauth2_provider')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
