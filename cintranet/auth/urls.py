from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cintranet.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', RedirectView.as_view(url='/')),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
)
