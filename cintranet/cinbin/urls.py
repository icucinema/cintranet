from django.conf.urls import include, url

from . import views

app_name = 'cinbin'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='cinbin_root'),
    url(r'^t/$', views.TextPasteCreateView.as_view(), name='cinbin_textpaste_create'),
    url(r'^t/(?P<slug>[a-z0-9\-]+)/$', views.TextPasteView.as_view(), name='cinbin_textpaste'),
    url(r'^t/(?P<slug>[a-z0-9\-]+)/delete/$', views.TextPasteDeleteView.as_view(), name='cinbin_textpaste_delete'),
    url(r'^i/$', views.ImagePasteCreateView.as_view(), name='cinbin_imagepaste_create'),
    url(r'^i/(?P<slug>[a-z0-9\-]+)/$', views.ImagePasteView.as_view(), name='cinbin_imagepaste'),
    url(r'^i/(?P<slug>[a-z0-9\-]+)/delete/$', views.ImagePasteDeleteView.as_view(), name='cinbin_imagepaste_delete'),
]