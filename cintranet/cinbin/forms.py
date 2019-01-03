from django import forms

from . import models

class TextPasteForm(forms.ModelForm):
    class Meta:
        model = models.TextPaste
        fields = ['content', 'public']

class ImagePasteForm(forms.ModelForm):
    class Meta:
        model = models.ImagePaste
        fields = ['content', 'public']