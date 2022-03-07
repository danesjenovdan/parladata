from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse

from parladata.models import Session, Link


class SessionLinkInline(admin.TabularInline):
    model = Link
    fk_name = 'session'
    exclude = ['person', 'membership', 'motion', 'question', 'organization', 'agenda_item']
    extra = 0

class SessionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['mandate', 'organizations']
    inlines = [
        SessionLinkInline
        # SpeechSessionInline,
        # MotionSessionInline,
    ]
    search_fields = ['name']
    list_display = ['id', 'name', 'tfidf', 'agenda_items', 'start_time']
    readonly_fields = ['created_at', 'updated_at']

    def tfidf(self, obj):
        partial_url = reverse('admin:parlacards_sessiontfidf_changelist')
        url = f'{settings.BASE_URL}{partial_url}?session__id__exact={obj.id}'
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    tfidf.allow_tags = True
    tfidf.short_description = 'TFIDF'

    def agenda_items(self, obj):
        partial_url = reverse('admin:parladata_agendaitem_changelist')
        url = f'{settings.BASE_URL}{partial_url}?session__id__exact={obj.id}'
        return mark_safe(f'<a href="{url}"><input type="button" value="Agenda items" /></a>')

    agenda_items.allow_tags = True
    agenda_items.short_description = 'Agenda items'


admin.site.register(Session, SessionAdmin)
