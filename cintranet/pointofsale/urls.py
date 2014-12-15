from django.conf.urls import patterns, include, url

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

router = routers.DefaultRouter()
router.register('tickets', views.TicketViewSet)
router.register('events', views.EventViewSet)
router.register('punters', views.PunterViewSet)
router.register('printers', views.PrinterViewSet)
urlpatterns = patterns('',
  url('^api-token-auth/', obtain_auth_token),
) + router.urls
