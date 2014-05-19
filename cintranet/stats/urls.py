from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='root'),
    url(r'^overview/audience/playweek/$', views.OverviewAudiencePlayweekView.as_view(), name='overview-audience-playweek'),
    url(r'^overview/audience/film/$', views.OverviewAudienceFilmView.as_view(), name='overview-audience-film'),
    url(r'^overview/money/$', views.OverviewMoneyView.as_view(), name='overview-money'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard/json/$', views.DashboardJsonView.as_view(), name='dashboard-json'),
)
