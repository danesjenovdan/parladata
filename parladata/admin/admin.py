from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import Q
from django import forms
from django.urls import reverse

from adminsortable2.admin import SortableAdminMixin

from parladata.models import *
from parladata.models.task import Task
from parladata.models.versionable_properties import *
from parladata.models.common import *
from parladata.admin.filters import SessionListFilter, PersonAuthorsListFilter, OrganizationAuthorsListFilter

from collections import Counter

from parladata.admin.link import *


class MandateAdmin(admin.ModelAdmin):
    list_display = ('description', 'beginning',)
    list_filter = ('description', 'beginning',)
    search_fields = ('description', 'beginning',)


class QuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'session']
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', SessionListFilter, PersonAuthorsListFilter, OrganizationAuthorsListFilter)
    fields = ['title', 'session', 'person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'recipient_text', 'type_of_question', 'timestamp', 'answer_timestamp', 'gov_id']
    readonly_fields = ['created_at', 'updated_at']


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_url']
    list_filter = ()

    readonly_fields = ['created_at', 'updated_at']

    def file_url(self, obj):
        return obj.file.url


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ['value']
    readonly_fields = ['created_at', 'updated_at']


class EducationLevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ('order',)
    list_display = ('id', 'text')
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']

# class PersonEducation(Person):
#     class Meta:
#         proxy = True

# class PersonEducationAdmin(admin.ModelAdmin):
#     list_display = ['name', 'education', 'number_of_mandates', 'education_level']
#     search_fields = ['name', 'number_of_mandates']
#     list_filter = ['education', 'number_of_mandates']
#     fields = ('name', 'education', 'education_level')


class BallotAdmin(admin.ModelAdmin):
    list_display = ['personvoter', 'option', 'vote']
    autocomplete_fields = ['personvoter', 'orgvoter', 'vote']
    list_filter = ('vote',)
    list_editable = ['option']
    readonly_fields = ['created_at', 'updated_at']

admin.site.site_header = _('Parladata')
admin.site.register(Task)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Mandate, MandateAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
