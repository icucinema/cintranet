from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf import settings

import sitewide.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cintranet.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', sitewide.views.IndexView.as_view()),
    url(r'^remoteheader/$', sitewide.views.RemoteHeaderView.as_view()),

    url(r'^user/', include('auth.urls', app_name='auth', namespace='auth')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^ticketing/', include('ticketing.urls')),
    url(r'^stats/', include('stats.urls', app_name='stats', namespace='stats')),
    url(r'^cinbin/', include('cinbin.urls', app_name='cinbin', namespace='cinbin')),
    url(r'^inventory/api/', include('inventory.api_urls')),
    url(r'^inventory/', include('inventory.urls', app_name='inventory', namespace='inventory')),
    url(r'^pointofsale/', include('pointofsale.urls', app_name='pointofsale', namespace='pointofsale')),
    url(r'^otp/', include('otp.urls', app_name='otp', namespace='otp')),
)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except (ImportError, AttributeError):
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

