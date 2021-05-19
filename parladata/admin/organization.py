from importlib import import_module

from django.contrib import admin

from parladata.models import Organization
from parladata.models.versionable_properties import *


class OrganizationNameInline(admin.TabularInline):
    model = OrganizationName
    extra = 0

class OrganizationAcronymInline(admin.TabularInline):
    model = OrganizationAcronym
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        # LinkPersonInline,
        OrganizationNameInline,
        OrganizationAcronymInline,
    ]
    search_fields = ('id',) # 'name' maybe?

admin.site.register(Organization, OrganizationAdmin)
