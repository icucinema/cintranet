from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views

app_name = 'auth'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/')),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^sso/$', views.SetAuthCookieView.as_view(), name='set_auth_cookie'),
]