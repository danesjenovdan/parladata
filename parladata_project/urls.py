from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
import debug_toolbar


from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # authentication
    path('oauth/', include(('oauth2_provider.urls', 'oauth'), namespace='oauth2_provider')),

    # admin views
    path('admin/', admin.site.urls),

    # REST api
    path('v3/', include(('parladata.urls', 'apiV3'), namespace='APIv3')),
    path('v3/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # card data api
    path('v3/cards/', include(('parlacards.urls', 'parlacards'), namespace='parlacards')),

    # legacy URLs
    path('v1/sandbox/', include(('sandbox.urls', 'sandobx'), namespace='sandbox')),

    # Django debug toolbar
    path('__debug__/', include(debug_toolbar.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
