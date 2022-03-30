from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

from import_export.admin import ExportMixin

from export.resources import MPResource

from parladata.models import Person, PersonMembership
from parladata.models.versionable_properties import *
from parladata.admin.link import LinkPersonSocialInline


class PersonNameInline(admin.TabularInline):
    model = PersonName
    extra = 0

class PersonHonorificPrefixInline(admin.TabularInline):
    model = PersonHonorificPrefix
    extra = 0

class PersonHonorificSuffixInline(admin.TabularInline):
    model = PersonHonorificSuffix
    extra = 0

class PersonPreferredPronounInline(admin.TabularInline):
    model = PersonPreferredPronoun
    extra = 0

class PersonEducationInline(admin.TabularInline):
    model = PersonEducation
    extra = 0

class PersonEducationLevelInline(admin.TabularInline):
    model = PersonEducationLevel
    extra = 0

class PersonPreviousOccupationInline(admin.TabularInline):
    model = PersonPreviousOccupation
    extra = 0

class PersonNumberOfMandatesInline(admin.TabularInline):
    model = PersonNumberOfMandates
    extra = 0

class PersonNumberOfVotersInline(admin.TabularInline):
    model = PersonNumberOfVoters
    extra = 0

class PersonEmailInline(admin.TabularInline):
    model = PersonEmail
    extra = 0

# class LinkPersonInline(admin.admin.TabularInline):
#     model = Link
#     fk_name = 'person'
#     exclude = ['organization', 'membership', 'motion', 'session', 'question']
#     extra = 0

class PersonAdmin(admin.ModelAdmin):
    inlines = [
        # LinkPersonInline,
        PersonNameInline,
        PersonHonorificPrefixInline,
        PersonHonorificSuffixInline,
        PersonPreferredPronounInline,
        PersonEducationInline,
        PersonEducationLevelInline,
        PersonPreviousOccupationInline,
        PersonNumberOfMandatesInline,
        PersonNumberOfVotersInline,
        PersonEmailInline,
        LinkPersonSocialInline,
    ]
    autocomplete_fields = ['districts']
    search_fields = ('id', 'personname__value', 'parser_names')
    list_display = ('id', 'name')
    readonly_fields = ['created_at', 'updated_at']

class ParliamentMember(Person):
    class Meta:
        proxy = True




class MPAdmin(ExportMixin, PersonAdmin):
    resource_class = MPResource
    list_display = ['id', 'name', 'tfidf', 'join_people']
    def get_queryset(self, request):
        MPs_ids = PersonMembership.objects.filter(role='voter').values_list('member', flat=True)
        qs = Person.objects.filter(id__in=MPs_ids)
        return qs

    def tfidf(self, obj):
        partial_url = reverse('admin:parlacards_persontfidf_changelist')
        url = f'{settings.BASE_URL}{partial_url}?member={obj.id}'
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    def join_people(self, obj):
        partial_url = '/admin/parladata/parliamentmember/mergepeople/'
        url = f'{settings.BASE_URL}{partial_url}?real_person={obj.id}'
        return mark_safe(f'<a href="{url}"><input type="button" value="Join people" /></a>')

    tfidf.allow_tags = True
    tfidf.short_description = 'TFIDF'

    join_people.allow_tags = True
    join_people.short_description = 'Join people'


admin.site.register(Person, PersonAdmin)
admin.site.register(ParliamentMember, MPAdmin)
