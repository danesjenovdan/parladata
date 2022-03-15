from django.contrib import admin
from django.forms import ModelForm, ChoiceField

from parladata.models.link import Link


PERSON_SOCIAL_NETWORK_CHOICES =(
    ("", ""),
    ("facebook", "facebook"),
    ("twitter", "twitter"),
)

ORGANIZATION_LINK_CHOICES =(
    ("", ""),
    ("facebook", "facebook"),
    ("twitter", "twitter"),
)

class SocialForm(ModelForm):
    note = ChoiceField(choices = PERSON_SOCIAL_NETWORK_CHOICES)
    class Meta:
        model = Link
        exclude = ['question', 'organization', 'motion', 'session', 'membership', 'agenda_item', 'legislation_consideration']


class OrganizationLinkForm(ModelForm):
    note = ChoiceField(choices = ORGANIZATION_LINK_CHOICES)
    class Meta:
        model = Link
        exclude = ['person', 'membership', 'motion', 'question', 'session', 'agenda_item', 'legislation_consideration']


class LinkOrganizationInline(admin.TabularInline):
    model = Link
    form = OrganizationLinkForm
    fk_name = 'organization'
    exclude = ['person', 'membership', 'motion', 'question', 'session', 'agenda_item', 'legislation_consideration']
    extra = 0


class LinkMembershipInline(admin.TabularInline):
    model = Link
    fk_name = 'membership'
    exclude = ['person', 'organization', 'motion', 'question', 'session', 'agenda_item', 'legislation_consideration']
    extra = 0


class LinkMotionInline(admin.TabularInline):
    model = Link
    fk_name = 'motion'
    exclude = ['person', 'membership', 'organization', 'session', 'question', 'agenda_item', 'legislation_consideration']
    extra = 0


class LinkQuestionInline(admin.TabularInline):
    model = Link
    fk_name = 'question'
    exclude = ['person', 'organization', 'motion', 'session', 'membership', 'agenda_item', 'legislation_consideration']
    extra = 0


class LinkPersonSocialInline(admin.TabularInline):
    model = Link
    form = SocialForm
    fk_name = 'person'
    exclude = ['question', 'organization', 'motion', 'session', 'membership', 'agenda_item', 'legislation_consideration']
    extra = 0


class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'name')
    autocomplete_fields = ['session', 'person', 'motion', 'question', 'agenda_item', 'organization', 'membership']
    fields = ['url', 'name', 'tags', 'session', 'agenda_item', 'motion', 'question', 'person', 'organization', 'membership', 'date', 'note']
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Link, LinkAdmin)
