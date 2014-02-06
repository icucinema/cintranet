from . import forms, models
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

class IndexView(RedirectView):
    def get_redirect_url(self):
        from django.core.urlresolvers import reverse
        return reverse('cinbin:cinbin_textpaste_create')

class RecentPastesMixin(object):
    def get_context_data(self, **kwargs):
        context = {}
        context['recent_text_pastes'] = models.TextPaste.objects.all()[0:5]
        context['recent_image_pastes'] = models.ImagePaste.objects.all()[0:5]
        context.update(kwargs)
        return super(RecentPastesMixin, self).get_context_data(**context)

class TextPasteCreateView(RecentPastesMixin, CreateView):
    template_name = 'cinbin/textpaste_create.html'
    form_class = forms.TextPasteForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class TextPasteView(RecentPastesMixin, DetailView):
    model = models.TextPaste
    pk_url_kwarg = 'id'
    template_name = 'cinbin/textpaste.html'

    def get_object(self, queryset=None):
        obj = super(TextPasteView, self).get_object(queryset)
        if not obj.public and not self.request.user.is_authenticated():
            raise PermissionDenied
        return obj

class TextPasteDeleteView(RecentPastesMixin, DeleteView):
    model = models.TextPaste
    pk_url_kwarg = 'id'
    success_url = '/cinbin/'

class ImagePasteCreateView(TextPasteCreateView):
    form_class = forms.ImagePasteForm
    template_name = 'cinbin/imagepaste_create.html'

class ImagePasteView(TextPasteView):
    model = models.ImagePaste
    template_name = 'cinbin/imagepaste.html'

class ImagePasteDeleteView(TextPasteDeleteView):
    model = models.ImagePaste
