from django.urls import include, path

from . import views

app_name = "stats"

urlpatterns = [
    path('', views.IndexView.as_view(), name='root'),
    path('overview/audience/playweek/', views.OverviewAudiencePlayweekView.as_view(), name='overview-audience-playweek'),
    path('overview/audience/film/', views.OverviewAudienceFilmView.as_view(), name='overview-audience-film'),
    path('overview/money/', views.OverviewMoneyView.as_view(), name='overview-money'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/json/', views.DashboardJsonView.as_view(), name='dashboard-json'),
    path('capacity/', views.CapacityDashboardView.as_view(), name='capacity'),
    path('capacity/json/', views.CapacityDashboardJsonView.as_view(), name='capacity-json'),
]