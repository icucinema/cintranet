from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.staticfiles.storage import staticfiles_storage

class IndexView(TemplateView):
    template_name = 'ticketing/index.html'

def angular_partial_view(request, partial):
    return HttpResponseRedirect(staticfiles_storage.url('ticketing/' + partial))