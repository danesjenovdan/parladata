from django.contrib import admin
from django.db import models

from parladata.models import AgendaItem, Link
from parladata.admin.filters import SessionListFilter

class LinkAgendaItemInline(admin.TabularInline):
    model = Link
    fk_name = 'agenda_item'
    exclude = ['person', 'organization', 'motion', 'session', 'membership', 'question']
    extra = 0


class AgendaItemAdmin(admin.ModelAdmin):
    inlines = [
        LinkAgendaItemInline,
    ]
    list_display = ('name', 'session', 'order')
    list_filter = (SessionListFilter,)
    search_fields = ['name', 'session__name']
    autocomplete_fields = ['session']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(AgendaItem, AgendaItemAdmin)
