from django.contrib import admin

from parladata.models import Link


class LinkOrganizationInline(admin.TabularInline):
    model = Link
    fk_name = 'organization'
    exclude = ['person', 'membership', 'motion', 'question', 'session', 'agenda_item']
    extra = 0


class LinkMembershipInline(admin.TabularInline):
    model = Link
    fk_name = 'membership'
    exclude = ['person', 'organization', 'motion', 'question', 'session', 'agenda_item']
    extra = 0


class LinkMotionInline(admin.TabularInline):
    model = Link
    fk_name = 'motion'
    exclude = ['person', 'membership', 'organization', 'session', 'question', 'agenda_item']
    extra = 0


class LinkQuestionInline(admin.TabularInline):
    model = Link
    fk_name = 'question'
    exclude = ['person', 'organization', 'motion', 'session', 'membership', 'agenda_item']
    extra = 0


class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'name')
    autocomplete_fields = ['session', 'person', 'motion', 'question', 'agenda_item', 'organization', 'membership']
    fields = ['url', 'name', 'tags', 'session', 'agenda_item', 'motion', 'question', 'person', 'organization', 'membership', 'date', 'note']
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Link, LinkAdmin)
