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


# class CountVoteInline(admin.TabularInline):
#     model = Count
#     fk_name = 'vote'
#     extra = 0


class SpeechSessionInline(admin.TabularInline):
    model = Speech
    autocomplete_fields = ['speaker', 'agenda_items', 'party']
    fk_name = 'session'
    extra = 0


# class MotionSessionInline(admin.TabularInline):
#     model = Motion
#     autocomplete_fields = ['person', 'organization', 'party']
#     fk_name = 'session'
#     extra = 0


class MandateAdmin(admin.ModelAdmin):
    list_display = ('description', 'beginning',)
    list_filter = ('description', 'beginning',)
    search_fields = ('description', 'beginning',)




class SpeechForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motions'].queryset = Motion.objects.filter(
            session=self.instance.session)

class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    fields = ['session', 'content', 'speaker', 'order', 'motions', 'start_time', 'tags', 'lemmatized_content']
    list_filter = (SessionListFilter, 'tags')
    search_fields = ['speaker__name', 'content']
    autocomplete_fields = ['motions', 'speaker', 'session']
    inlines = []
    list_display = ('id',
                    'tag_list',
                    'session_name',
                    'speaker')
    list_per_page = 25
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple()},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags', 'session', 'speaker')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def session_name(self, obj):
        return obj.session.name


class QuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'session']
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', SessionListFilter, PersonAuthorsListFilter, OrganizationAuthorsListFilter)
    fields = ['title', 'session', 'person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'recipient_text', 'type_of_question', 'timestamp', 'answer_timestamp']


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_url']
    list_filter = ()

    def file_url(self, obj):
        return obj.file.url


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ['value']


class EducationLevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ('order',)
    list_display = ('id', 'text')
    search_fields = ['text']

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


admin.site.register(Speech, SpeechAdmin)
admin.site.register(Task)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Mandate, MandateAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
