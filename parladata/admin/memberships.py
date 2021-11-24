from django.contrib import admin

from parladata.admin.link import *
from parladata.models import *
from parladata.admin.filters import AllOrganizationsListFilter, AllOnBehalfOfListFilter


class MembershipAdmin(admin.ModelAdmin):
    inlines = [
        LinkMembershipInline,
    ]
    list_filter = ['role', AllOrganizationsListFilter, AllOnBehalfOfListFilter]
    search_fields = ['member__personname__value', 'role', 'on_behalf_of__organizationname__value', 'organization__organizationname__value']
    autocomplete_fields = ('member', 'organization', 'on_behalf_of')

    # set order of fields in the dashboard
    fields = ['member', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate']


admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(OrganizationMembership)
