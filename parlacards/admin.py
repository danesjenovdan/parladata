from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from parlacards.models import (SessionTfidf, PersonTfidf, GroupTfidf)
from parladata.models.memberships import PersonMembership

from django.contrib import admin

from datetime import datetime


class MembersListFilter(admin.SimpleListFilter):
    title = 'member'

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        list_of_members = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('member__personname').filter(
            role='voter'
        ).values('member_id', 'member__personname__value')

        for breed in queryset:
            list_of_members.append(
                (str(breed['member_id']), breed['member__personname__value'])
            )
        return sorted(list_of_members, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person_id=self.value())
        return queryset


class OrganizationsListFilter(admin.SimpleListFilter):
    title = 'organization'

    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        list_of_members = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('on_behalf_of__organizationname__value').filter(
            role='voter'
        ).order_by('on_behalf_of', 'on_behalf_of__organizationname__value').distinct('on_behalf_of').values('on_behalf_of_id', 'on_behalf_of__organizationname__value')

        for breed in queryset:
            list_of_members.append(
                (str(breed['on_behalf_of_id']), breed['on_behalf_of__organizationname__value'])
            )
        return sorted(list_of_members, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(group_id=self.value())
        return queryset


class SessionTfidfAdmin(admin.ModelAdmin):
    list_display = ('session_name', 'token', 'value', 'created_at', 'delete')
    list_filter = ('session',)
    search_fields = ['session__name']
    list_per_page = 20
    ordering = ['timestamp__date', '-value']
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
    list_display = ( 'person', 'token', 'value', 'created_at', 'delete')
    list_filter = (MembersListFilter, )
    list_per_page = 20
    ordering = ['timestamp__date', '-value']
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
    list_display = ('group', 'token', 'value', 'created_at', 'delete')
    list_filter = (OrganizationsListFilter, )
    list_per_page = 20
    ordering = ['timestamp__date', '-value']
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
