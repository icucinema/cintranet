from django.shortcuts import render
from django.views.generic import TemplateView

from . import providers

class IndexView(TemplateView):
    template_name = 'otp/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['providers'] = providers.PROVIDERS
        return context
