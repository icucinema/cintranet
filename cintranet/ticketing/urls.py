from django.conf.urls import patterns, include, url

from rest_framework import routers

from . import api_views, views

api_router = routers.DefaultRouter()
api_router.register(r'punters', api_views.PunterViewSet)

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='root'),
    url(r'^(?P<partial>partials/[a-z]+\.html)$', views.angular_partial_view),
    #url(r'^api/', include(api_router.urls)),
    # need to work around an issue in rest_framework
    # so this is declared at the top level
)
api_urlpatterns = api_router.urls