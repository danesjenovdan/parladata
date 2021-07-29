from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from parlacards.models import (SessionTfidf, PersonTfidf, GroupTfidf)


class SessionTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'session_name', 'token', 'value', 'delete')
    list_filter = ('session',)
    search_fields = ['session__name']
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)

    def get_queryset(self, request):
        return SessionTfidf.objects.all().prefetch_related('session')

    def session_name(self, obj):
        return obj.session.name

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields['token'].widget.attrs['rows'] = 1
        data.form.base_fields['token'].widget.attrs['cols'] = 25
        data.form.base_fields['token'].widget.attrs.pop('class')
        return data

    def delete(self, obj):
        return mark_safe(f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />')

    delete.allow_tags = True
    delete.short_description = 'Delete object'


class PersonTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'person', 'token', 'value', 'delete')
    list_filter = ('person',)
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields['token'].widget.attrs['rows'] = 1
        data.form.base_fields['token'].widget.attrs['cols'] = 25
        data.form.base_fields['token'].widget.attrs.pop('class')
        return data

    def delete(self, obj):
        return mark_safe(f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />')

    delete.allow_tags = True
    delete.short_description = 'Delete object'


class GroupTfidfAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'group', 'token', 'value', 'delete')
    list_filter = ('group',)
    list_per_page = 20
    ordering = ['-value']
    list_editable = ('token',)

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields['token'].widget.attrs['rows'] = 1
        data.form.base_fields['token'].widget.attrs['cols'] = 25
        data.form.base_fields['token'].widget.attrs.pop('class')
        return data

    def delete(self, obj):
        return mark_safe(f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />')

    delete.allow_tags = True
    delete.short_description = 'Delete object'


admin.site.register(SessionTfidf, SessionTfidfAdmin)
admin.site.register(PersonTfidf, PersonTfidfAdmin)
admin.site.register(GroupTfidf, GroupTfidfAdmin)
