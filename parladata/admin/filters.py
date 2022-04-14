from django.contrib import admin

from parladata.models.memberships import PersonMembership
from parladata.models.session import Session
from parladata.models.organization import Organization

from datetime import datetime


class MembersListFilter(admin.SimpleListFilter):
    title = 'member'

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        list_of_members = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('member__personname').filter(
            role='voter'
        ).values('member_id', 'member__personname__value')

        for person in queryset:
            list_of_members.append(
                (str(person['member_id']), person['member__personname__value'])
            )
        return sorted(list_of_members, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person_id=self.value())
        return queryset


class MembershipMembersListFilter(MembersListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(member_id=self.value())
        return queryset

class MembersAndLeaderListFilter(admin.SimpleListFilter):
    title = 'member_or_leader'

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        list_of_members = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('member__personname').filter(
            role__in=['voter', 'leader']
        ).values(
            'member_id',
            'member__personname__value'
        )

        for person in queryset:
            list_of_members.append(
                (str(person['member_id']), person['member__personname__value'])
            )
        return sorted(list_of_members, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person_id=self.value())
        return queryset


class PersonAuthorsListFilter(MembersListFilter):
    title = 'person_authors'

    parameter_name = 'person_authors'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person_authors__id=self.value())
        return queryset


class OrganizationsListFilter(admin.SimpleListFilter):
    title = 'organization'

    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        list_of_groups = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('on_behalf_of__organizationname__value').filter(
            role='voter'
        ).exclude(on_behalf_of=None).order_by('on_behalf_of', 'on_behalf_of__organizationname__value').distinct('on_behalf_of').values('on_behalf_of_id', 'on_behalf_of__organizationname__value')

        for group in queryset:
            list_of_groups.append(
                (str(group['on_behalf_of_id']), group['on_behalf_of__organizationname__value'])
            )
        return sorted(list_of_groups, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(group_id=self.value())
        return queryset


class OrganizationAuthorsListFilter(OrganizationsListFilter):
    title = 'organization_authors'

    parameter_name = 'organization_authors'

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(organization_authors=self.value())
        return queryset


class RoleListFilter(admin.SimpleListFilter):
    title = 'role'

    parameter_name = 'role'

    def lookups(self, request, model_admin):
        list_of_groups = []
        queryset = PersonMembership.valid_at(datetime.now()).prefetch_related('on_behalf_of__organizationname__value').filter(
            role='voter'
        ).order_by('on_behalf_of', 'on_behalf_of__organizationname__value').distinct('on_behalf_of').values('on_behalf_of_id', 'on_behalf_of__organizationname__value')

        for group in queryset:
            list_of_groups.append(
                (str(group['on_behalf_of_id']), group['on_behalf_of__organizationname__value'])
            )
        return (
            ('member', 'member'),
            ('voter', 'voter'),
            ('president', 'president'),
            ('deputy', 'deputy'),
            ('leader', 'leader'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(role=self.value())
        return queryset


class AllOrganizationsListFilter(admin.SimpleListFilter):
    title = 'organization'

    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        list_of_groups = []
        queryset = Organization.objects.all().values('id', 'organizationname__value')

        for group in queryset:
            if group['organizationname__value']:
                list_of_groups.append(
                    (str(group['id']), group['organizationname__value'])
                )
        return sorted(list_of_groups, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(organization_id=self.value())
        return queryset


class AllOnBehalfOfListFilter(OrganizationsListFilter):
    title = 'on_behalf_of'
    parameter_name = 'on_behalf_of'

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(on_behalf_of_id=self.value())
        return queryset


class SessionListFilter(admin.SimpleListFilter):
    title = 'session'

    parameter_name = 'session'

    def lookups(self, request, model_admin):
        list_of_sessions = []
        list_of_sessions = [(str(session['id']), session['name']) for session in Session.objects.all().order_by('start_time').values('id', 'name')]

        return list_of_sessions

    def queryset(self, request, queryset):
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(session_id=self.value())
        return queryset


class ParsableFilter(admin.SimpleListFilter):
    title = 'parsable'

    parameter_name = 'parsable'

    def lookups(self, request, model_admin):
        list_of_members = []

        return [['parsable', 'parsable'], ['parsed', 'parsed']]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__name=self.value())
        return queryset
