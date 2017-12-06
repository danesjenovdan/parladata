from django.conf.urls import patterns, include, url

from django.contrib import admin
from parladata.views import index

#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'parladata.views.index', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #(r'^$', index),
    (r'^admin/', include(admin.site.urls)),
    (r'^v1/', include('parladata.urls')),
    (r'^v1/tasks/', include('parlasearch.urls')),
    (r'^v1/sandbox/', include('sandbox.urls')),

)
