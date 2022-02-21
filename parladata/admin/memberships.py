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
    list_display = ['member__personname__value', 'organization__organizationname__value', 'role', 'start_time', 'end_time']

    # set order of fields in the dashboard
    fields = ['member', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate']
    readonly_fields = ['created_at', 'updated_at']


class OrganizationMembershipAdmin(admin.ModelAdmin):
    autocomplete_fields = ('member', 'organization')
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(OrganizationMembership, OrganizationMembershipAdmin)
