from django.conf.urls import patterns, include, url

from . import api_views, views, api_router

api_router = api_router.APIRouter()
api_router.register(r'punters', api_views.PunterViewSet)
api_router.register(r'films', api_views.FilmViewSet)
api_router.register(r'entitlements', api_views.EntitlementViewSet)
api_router.register(r'entitlement-details', api_views.EntitlementDetailViewSet)
api_router.register(r'ticket-types', api_views.TicketTypeViewSet)
api_router.register(r'tickets', api_views.TicketViewSet)
api_router.register(r'ticket-templates', api_views.TicketTemplateViewSet)
api_router.register(r'event-types', api_views.EventTypeViewSet)
api_router.register(r'showings', api_views.ShowingViewSet)
api_router.register(r'events', api_views.EventViewSet)

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='root'),
    url(r'^(?P<partial>partials/[a-z]+\.html)$', views.angular_partial_view),
    url(r'^api/films/(?P<film_id>[0-9]+)/bor-data/(?P<show_week>20[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2})/$', views.generate_bor_information),
    url(r'^api/films/(?P<film_id>[0-9]+)/generate-bor-pdf/(?P<show_week>20[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2})/$', views.generate_bor_draft_pdf),
    #url(r'^api/', include(api_router.urls)),
    # need to work around an issue in rest_framework
    # so this is declared at the top level
)
api_urlpatterns = api_router.urls
