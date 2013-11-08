import random
import string

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from . import forms

class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        if request.session.get('logout_token', '') == request.GET.get('token', ''):
            logout(request)
            messages.info(request, u"You have been logged out successfully!")
        else:
            messages.error(request, u"Security token error.")
        return super(LogoutView, self).get(request, *args, **kwargs)

class LoginView(FormView):
    template_name = 'auth/login.html'
    success_url = '/'
    form_class = forms.LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
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
            return super(LoginView, self).form_valid(form)
        else:
            form._errors['username'] = [u'Your username or password were incorrect.']
            return super(LoginView, self).form_invalid(form)