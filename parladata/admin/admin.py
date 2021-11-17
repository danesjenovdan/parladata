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
from parladata.admin.filters import SessionListFilter, AuthorsListFilter

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
    fields = ['content', 'motions', 'speaker', 'order', 'tags', 'session', 'lemmatized_content']
    list_filter = (SessionListFilter, 'tags')
    search_fields = ['speaker__name', 'content']
    autocomplete_fields = ['motions', 'speaker', 'session']
    inlines = [
    ]
    list_display = ('id',
                    'tag_list',
                    'session_name',
                    'speaker')
    list_per_page = 25
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple(attrs={'style': 'width: 100%'})},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags', 'session', 'speaker')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def session_name(self, obj):
        return obj.session.name


class QuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['authors', 'recipient_people', 'recipient_organizations', 'session']
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', SessionListFilter, AuthorsListFilter)


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


class LawAdmin(admin.ModelAdmin):
    list_display = ('text', 'session', 'status', 'epa')
    list_filter = (SessionListFilter,)
    search_fields = ['text']
    autocomplete_fields = ('session', 'mdt_fk')


class BallotAdmin(admin.ModelAdmin):
    list_display = ('vote', 'personvoter', 'option')
    autocomplete_fields = ['personvoter', 'orgvoter', 'vote']



admin.site.register(Speech, SpeechAdmin)
admin.site.register(Task)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Law, LawAdmin)
admin.site.register(Mandate, MandateAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
