from rest_framework import routers
from django.conf.urls import url, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register('tickets', views.TicketViewSet)
router.register('events', views.EventViewSet)
router.register('punters', views.PunterViewSet)
router.register('printers', views.PrinterViewSet)

urlpatterns = [
  url('^api-token-auth/', obtain_auth_token),
] + router.urls
