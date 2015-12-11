from django.contrib import admin
from django.utils import timezone

from .models import Printer, FilmQuotation

admin.site.register(Printer)

def fq_set_valid_to_now(modeladmin, request, queryset):
    queryset.update(valid_to=timezone.now())
fq_set_valid_to_now.short_description = "Set valid to date to now on selected quotations"

def fq_disable(modeladmin, request, queryset):
    queryset.update(enabled=False)
fq_disable.short_description = "Disable selected quotations"

def fq_enable(modeladmin, request, queryset):
    queryset.update(enabled=True)
fq_enable.short_description = "Enable selected quotations"

class FilmQuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation', 'film_title', 'usable', 'enabled', 'valid_from', 'valid_to']
    actions = [fq_set_valid_to_now, fq_disable, fq_enable]

admin.site.register(FilmQuotation)
