import random
import string

from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.core import signing
from django.contrib.auth import authenticate, login, logout
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from . import forms

class SetAuthCookieMixin(object):
    signing_key = settings.SSO_SHARED_SECRET_KEY
    cookie_settings = settings.SSO_COOKIE_SETTINGS

    def set_cookie(self, resp):
        cookie_data = signing.dumps(self.generate_session_data(), key=self.signing_key, salt='icuc_auth')
        resp.set_cookie('icuc_auth', cookie_data, **self.cookie_settings)
        return resp

    def generate_session_data(self):
        u = self.request.user
        self.request.session['has_session'] = True
        sess_cookie = settings.SESSION_COOKIE_NAME
        sess_id = self.request.session.session_key
        return {
            'session_cookie': sess_cookie,
            'session_id': sess_id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'name': '%s %s' % (u.first_name, u.last_name)
        }

class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        if request.session.get('logout_token', '') == request.GET.get('token', ''):
            logout(request)
            messages.info(request, u"You have been logged out successfully!")
        else:
            messages.error(request, u"Security token error.")
        resp = super(LogoutView, self).get(request, *args, **kwargs)
        resp.delete_cookie('icuc_auth', domain=settings.SSO_COOKIE_SETTINGS.get('domain', None), path=settings.SSO_COOKIE_SETTINGS.get('path', '/'))
        return resp

class LoginView(SetAuthCookieMixin, FormView):
    template_name = 'auth/login.html'
    form_class = forms.LoginForm
    
    def get_success_url(self):
        return self.request.POST.get('next', self.request.GET.get('next', '/'))
        
    def get_context_data(self, **kwargs):
        cd = super(LoginView, self).get_context_data(**kwargs)
        cd.setdefault('next', self.get_success_url())
        return cd

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user is not None and user.is_active:
            login(self.request, user)
            self.request.session['logout_token'] = ''.join([random.choice(string.ascii_letters) for n in range(32)])
            messages.success(self.request, u"Welcome back, {}!".format(user.first_name))
            resp = super(LoginView, self).form_valid(form)
            self.set_cookie(resp)
            return resp
        else:
            form._errors['username'] = [u'Your username or password were incorrect.']
            return super(LoginView, self).form_invalid(form)

class SetAuthCookieView(SetAuthCookieMixin, RedirectView):
    def get(self, *args, **kwargs):
        return self.set_cookie(super(SetAuthCookieView, self).get(*args, **kwargs))

    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get('next', '/')

