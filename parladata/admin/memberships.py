from django.contrib import admin
from django import forms
from django.db.models import Q

from parladata.admin.link import *
from parladata.models import *
from parladata.admin.filters import AllOrganizationsListFilter, AllOnBehalfOfListFilter, MembershipMembersListFilter
from export.resources.misc import MembershipResource

from import_export.admin import ImportExportModelAdmin





class PersonMembershipForm(forms.ModelForm):
    class Meta:
        model = PersonMembership
        exclude = []

    def clean(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        member = self.cleaned_data.get('member')
        organization = self.cleaned_data.get('organization')
        memberships = PersonMembership.objects.filter(
            member=member,
            organization=organization,
        )
        print('CLEAN')
        # check for overlapping memberships
        if end_time:
            # check if new membership ends inside existing membership
            if memberships.filter(
                    Q(start_time__lte=end_time) |
                    Q(start_time=None),
                    Q(end_time__gte=end_time) |
                    Q(end_time=None)
                ).exclude(
                    pk=self.instance.pk
                ).exists():
                raise forms.ValidationError("This membership ends inside existing membership")

            if start_time:
                # check new membership starts before and end afret existing membership
                if memberships.filter(
                        start_time__lte=start_time,
                        end_time__gte=end_time
                    ).exclude(
                        pk=self.instance.pk
                    ).exists():
                    raise forms.ValidationError("Membership is around existing membership")

        if start_time:
            if memberships.filter(
                    Q(start_time__lte=start_time) |
                    Q(start_time=None),
                    Q(end_time__gte=start_time) |
                    Q(end_time=None)
                ).exclude(
                    pk=self.instance.pk
                ).exists():
                raise forms.ValidationError("This membership starts inside existing membership")

        if not start_time and not end_time and memberships.exists():
            raise forms.ValidationError("Membership must have start or end time if there is membership with same member and organization")

        return self.cleaned_data

class MembershipAdmin(ImportExportModelAdmin):
    resource_classes = [MembershipResource]

    form = PersonMembershipForm

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
    search_fields = ['member__organizationname__value', 'organization__organizationname__value']
    list_filter = ['mandate', AllOrganizationsListFilter]


admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(OrganizationMembership, OrganizationMembershipAdmin)
