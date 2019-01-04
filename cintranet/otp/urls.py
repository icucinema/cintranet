from django.conf.urls import include, url

from otp import views

urlpatterns = [
        url(r'^$', views.IndexView.as_view(), name='root'),
]

