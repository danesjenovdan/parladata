from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import Q
from django import forms
from django.urls import reverse

from parladata.models import *
from parladata.models.task import Task
from parladata.models.versionable_properties import *

from collections import Counter



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

class MembershipAdmin(admin.ModelAdmin):
    inlines = [
        LinkMembershipInline,
    ]
    list_filter = ['role', 'organization', 'on_behalf_of']
    search_fields = ['member__personname__value', 'role', 'on_behalf_of__organizationname__value', 'organization__organizationname__value']
    autocomplete_fields = ('member', 'organization', 'on_behalf_of')


class SpeechForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motions'].queryset = Motion.objects.filter(
            session=self.instance.session)

class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    fields = ['content', 'motions', 'speaker', 'order', 'tags', 'session']
    list_filter = ('session', 'tags')
    search_fields = ['speaker__name', 'content']
    autocomplete_fields = ['motions', 'speaker']
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
    autocomplete_fields = ['authors']
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', 'session', 'authors')


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_url']
    list_filter = ()

    def file_url(self, obj):
        return obj.file.url


class MotionAdmin(admin.ModelAdmin):
    #form = MotionForm
    list_display = (
        'id',
        'text',
        'session_name',
        'result',
        'requirement',
        'get_for',
        'get_against',
        'get_abstain',
        'get_not',
        'link_to_vote',
        'datetime',
    )

    list_editable = ('result',)
    list_filter = ('result', 'datetime', 'session')
    search_fields = ['text', 'title']
    inlines = [
        LinkMotionInline,
    ]
    list_per_page = 25

    def get_queryset(self, request):
        return Motion.objects.all().prefetch_related('session', 'vote').order_by('-id')

    def get_for(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("for", 0)
        return results

    def get_against(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("against", 0)
        return results

    def get_abstain(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("abstain", 0)
        return results

    def get_not(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("absent", 0)
        return results

    def link_to_vote(self, obj):
        try:
            link = reverse("admin:parladata_vote_change", args=[obj.vote.first().id])
        except:
            return ''
        return mark_safe(f'<a href="{link}">Vote</a>')

    def session_name(self, obj):
        return obj.session.name if obj.session else ''


    link_to_vote.allow_tags = True

    get_for.short_description = 'for'
    get_against.short_description = 'against'
    get_abstain.short_description = 'abstain'
    get_not.short_description = 'absent'

    def get_search_results(self, request, queryset, search_term):
        url = request.META.get('HTTP_REFERER', '')

        # if autocompelte calls from speech admin then filter motions by speech session
        if '/admin/parladata/speech/' in url:
            speech_id = url.split('/')[-3]
            session = Speech.objects.get(id=speech_id).session
            queryset = queryset.filter(session=session)

        results = super().get_search_results(
            request,
            queryset,
            search_term
        )
        return results





class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')

    search_fields = ['value']


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
    list_filter = ('session',)
    search_fields = ['text']


class BallotAdmin(admin.ModelAdmin):
    list_display = ('vote', 'personvoter', 'option')
    autocomplete_fields = ['personvoter', 'orgvoter', 'vote']


admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Motion, MotionAdmin)
#admin.site.register(Area, LeafletGeoAdmin)
admin.site.register(Link)
admin.site.register(Task)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Law, LawAdmin)
admin.site.register(OrganizationMembership)
admin.site.register(Mandate, MandateAdmin)
admin.site.register(Document, DocumentAdmin)
