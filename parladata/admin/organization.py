from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

from parladata.models import Organization, Link, PersonMembership
from parladata.models.versionable_properties import *


class OrganizationNameInline(admin.TabularInline):
    model = OrganizationName
    extra = 0

class OrganizationAcronymInline(admin.TabularInline):
    model = OrganizationAcronym
    extra = 0

class OrganizationEmailInline(admin.TabularInline):
    model = OrganizationEmail
    extra = 0

class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        # LinkPersonInline,
        OrganizationNameInline,
        OrganizationAcronymInline,
        OrganizationEmailInline
    ]
    search_fields = ('id', 'organizationname__value') # 'name' maybe?

    list_display = ('id', 'name', 'tfidf')

    def tfidf(self, obj):
        partial_url = reverse('admin:parlacards_grouptfidf_changelist')
        url = f'{settings.BASE_URL}{partial_url}?organization={obj.id}'
        return mark_safe(f'<input onclick="location.href=\'{url}\'" type="button" value="Tfidf" />')

    tfidf.allow_tags = True
    tfidf.short_description = 'TFIDF'


class ParliamentaryGroup(Organization):
    class Meta:
        proxy = True


class ParliamentaryGroupAdmin(OrganizationAdmin):
    list_display = ('id', 'name', 'tfidf')
    def get_queryset(self, request):
        group_ids = PersonMembership.objects.filter(role='voter').values_list('on_behalf_of', flat=True)
        qs = Organization.objects.filter(id__in=group_ids)
        return qs

    def tfidf(self, obj):
        partial_url = reverse('admin:parlacards_grouptfidf_changelist')
        url = f'{settings.BASE_URL}{partial_url}?organization={obj.id}'
        return mark_safe(f'<input onclick="location.href=\'{url}\'" type="button" value="Tfidf" />')

    tfidf.allow_tags = True
    tfidf.short_description = 'TFIDF'

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(ParliamentaryGroup, ParliamentaryGroupAdmin)
