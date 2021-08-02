from importlib import import_module

from django.contrib import admin

from parladata.models import Person, PersonMembership
from parladata.models.versionable_properties import *

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
    ]
    search_fields = ('id', 'personname__value')
    list_display = ('id', 'name')

class ParliamentMember(Person):
    class Meta:
        proxy = True


class MPAdmin(PersonAdmin):
    def get_queryset(self, request):
        MPs_ids = PersonMembership.objects.filter(role='voter').values_list('member', flat=True)
        qs = Person.objects.filter(id__in=MPs_ids)
        if request.user.is_superuser:
            return qs


admin.site.register(Person, PersonAdmin)
admin.site.register(ParliamentMember, MPAdmin)
