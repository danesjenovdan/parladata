from django.contrib import admin

from parladata.admin.link import *
from parladata.models import *
from parladata.admin.filters import AllOrganizationsListFilter, AllOnBehalfOfListFilter, MembershipMembersListFilter


class MembershipAdmin(admin.ModelAdmin):
    inlines = [
        LinkMembershipInline,
    ]
    list_filter = ['role', 'mandate', MembershipMembersListFilter, AllOrganizationsListFilter, AllOnBehalfOfListFilter]
    search_fields = ['member__personname__value', 'role', 'on_behalf_of__organizationname__value', 'organization__organizationname__value']
    autocomplete_fields = ('member', 'organization', 'on_behalf_of')
    list_display = ['member_name', 'organization_name', 'role', 'start_time', 'end_time']

    # set order of fields in the dashboard
    fields = ['member', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 15

    def member_name(self, obj):
        try:
            return obj.member.personname.last().value
        except:
            return obj.member.name

    def organization_name(self, obj):
        try:
            return obj.organization.organizationname.last().value
        except:
            return obj.organization.name

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('member', 'organization', 'member__personname')

class OrganizationMembershipAdmin(admin.ModelAdmin):
    autocomplete_fields = ('member', 'organization')
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(OrganizationMembership, OrganizationMembershipAdmin)
