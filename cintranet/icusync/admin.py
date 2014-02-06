from django.contrib import admin
from . import models

admin.site.register(models.SKU)
admin.site.register(models.Product)
admin.site.register(models.SKUEntitlement)

class AuthenticationCredentialAdmin(admin.ModelAdmin):
    list_display = ('auth_slug', )
admin.site.register(models.AuthenticationCredential, AuthenticationCredentialAdmin)
