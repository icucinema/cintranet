from django.conf.urls import patterns, include, url

from . import api_views, views

from rest_framework import routers

api_router = routers.DefaultRouter()
api_router.register(r'punters', api_views.PunterViewSet)
api_router.register(r'films', api_views.FilmViewSet)
api_router.register(r'entitlements', api_views.EntitlementViewSet)
api_router.register(r'entitlement-details', api_views.EntitlementDetailViewSet)
api_router.register(r'ticket-types', api_views.TicketTypeViewSet)
api_router.register(r'tickets', api_views.TicketViewSet)
api_router.register(r'ticket-templates', api_views.TicketTemplateViewSet)
api_router.register(r'showings-weeks', api_views.ShowingsWeekViewSet)
api_router.register(r'event-types', api_views.EventTypeViewSet)
api_router.register(r'showings', api_views.ShowingViewSet)
api_router.register(r'events', api_views.EventViewSet)
api_router.register(r'distributors', api_views.DistributorViewSet)
api_router.register(r'punter-identifiers', api_views.PunterIdentifierViewSet)

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='root'),
    url(r'^(?P<partial>partials/[a-z]+\.html)$', views.angular_partial_view),
    url(r'^events/ical/$', views.EventCalendar(), name='event_calendar'),
    url(r'^api/films/(?P<film_id>[0-9]+)/bor-data/(?P<show_week>20[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2})/$', views.generate_bor_information),
    url(r'^api/films/(?P<film_id>[0-9]+)/generate-bor-pdf/(?P<show_week>20[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2})/$', views.generate_bor_draft_pdf),
    url(r'^api/', include(api_router.urls)),
    # need to work around an issue in rest_framework
    # so this is declared at the top level
)
