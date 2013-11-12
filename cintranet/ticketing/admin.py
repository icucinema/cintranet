from django.contrib import admin
from . import models

class PunterAdmin(admin.ModelAdmin):
    list_display = ('name', 'punter_type', 'cid', 'email')
admin.site.register(models.Punter, PunterAdmin)

class FilmAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(models.Film, FilmAdmin)

admin.site.register(models.Showing)
admin.site.register(models.EventType)
admin.site.register(models.Event)

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'sale_price')
admin.site.register(models.TicketType, TicketTypeAdmin)

class TicketTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'sale_price', 'sell_online', 'sell_on_the_door', 'general_availability')
admin.site.register(models.TicketTemplate, TicketTemplateAdmin)

class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('punter', 'entitled_to', 'valid')
admin.site.register(models.Entitlement, EntitlementAdmin)

admin.site.register(models.Ticket)