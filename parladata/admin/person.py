from importlib import import_module

from django.contrib import admin

from parladata.models import Person
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
    ]
    search_fields = ('id',) # 'name' maybe?

admin.site.register(Person, PersonAdmin)
