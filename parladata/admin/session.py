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
    list_display = ['id', 'name', 'tfidf', 'start_time']
    readonly_fields = ['created_at', 'updated_at']

    def tfidf(self, obj):
        partial_url = reverse('admin:parlacards_sessiontfidf_changelist')
        url = f'{settings.BASE_URL}{partial_url}?session__id__exact={obj.id}'
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    tfidf.allow_tags = True
    tfidf.short_description = 'TFIDF'


admin.site.register(Session, SessionAdmin)
