from django.contrib import admin
from . import models

admin.site.register(models.TextPaste)
admin.site.register(models.ImagePaste)
