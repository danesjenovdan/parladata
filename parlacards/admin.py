from django.contrib import admin

from parlacards.models import (SessionTfidf, PersonTfidf, GroupTfidf)


class SessionTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'session_name', 'token', 'value')
    list_filter = ('session',)
    search_fields = ['session__name']
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)

    def get_queryset(self, request):
        return SessionTfidf.objects.all().prefetch_related('session')

    def session_name(self, obj):
        return obj.session.name


class PersonTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'person', 'token', 'value')
    list_filter = ('person',)
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)


class GroupTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'group', 'token', 'value')
    list_filter = ('group',)
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)


admin.site.register(SessionTfidf, SessionTfidfAdmin)
admin.site.register(PersonTfidf, PersonTfidfAdmin)
admin.site.register(GroupTfidf, GroupTfidfAdmin)
