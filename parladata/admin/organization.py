from importlib import import_module

from django.contrib import admin

from parladata.models import Organization, Link
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

admin.site.register(Organization, OrganizationAdmin)
