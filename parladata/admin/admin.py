from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import Q
from django import forms
from django.urls import reverse

from parladata.models import *
from parladata.models.versionable_properties import *

from collections import Counter

class LinkOrganizationInline(admin.TabularInline):
    model = Link
    fk_name = 'organization'
    exclude = ['person', 'membership', 'motion', 'question', 'session']
    extra = 0


class LinkMembershipInline(admin.TabularInline):
    model = Link
    fk_name = 'membership'
    exclude = ['person', 'organization', 'motion', 'question', 'session']
    extra = 0


class LinkMotionInline(admin.TabularInline):
    model = Link
    fk_name = 'motion'
    exclude = ['person', 'membership', 'organization', 'session', 'question']
    extra = 0


class LinkQuestionInline(admin.TabularInline):
    model = Link
    fk_name = 'question'
    exclude = ['person', 'organization', 'motion', 'session', 'membership']
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
    # list_filter = ['organization']
    search_fields = ['member__name', 'organization___name']
    autocomplete_fields = ('member', 'organization', 'on_behalf_of')


class SessionAdmin(admin.ModelAdmin):
    # autocomplete_fields = ['mandate', 'organization', 'organizations']
    inlines = [
        # SpeechSessionInline,
        # MotionSessionInline,
    ]
    search_fields = ['name']

class SpeechForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motions'].queryset = Motion.objects.filter(
            session=self.instance.session)

class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    fields = ['content', 'motions', 'speaker', 'order', 'tags']
    list_filter = ('session', 'tags')
    search_fields = ['speaker__name', 'content']
    #autocomplete_fields = ['motion']
    inlines = [
    ]
    list_display = ('id',
                    'tag_list',
                    'session_name',
                    'speaker')
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags', 'session', 'speaker')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def session_name(self, obj):
        return obj.session.name


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', 'session', 'authors')


class MotionAdmin(admin.ModelAdmin):
    #form = MotionForm
    list_display = ('id',
                    'text',
                    'datetime',
                    'result',
                    'requirement',
                    'get_for',
                    'get_against',
                    'get_abstain',
                    'get_not',
                    'link_to_vote',
                    'session_name')

    list_editable = ('result',)
    list_filter = ('result', 'datetime', 'session')
    search_fields = ['text', 'vote__session__name']
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
        link = reverse("admin:parladata_vote_change", args=[obj.vote.first().id])
        return mark_safe(f'<a href="{link}">Vote</a>')

    def session_name(self, obj):
        return obj.session.name if obj.session else ''

    link_to_vote.allow_tags = True

    get_for.short_description = 'for'
    get_against.short_description = 'against'
    get_abstain.short_description = 'abstain'
    get_not.short_description = 'absent'


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', )

    list_filter = ('tags',)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ['name']

    def the_tags(self, obj):
        return "%s" % (obj.tags.all(), )
    the_tags.short_description = 'tags'


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


class ParliamentMember(Person):
    class Meta:
        proxy = True


class MPAdmin(admin.ModelAdmin):
    # TODO bring back name
    # list_display = ('name',)
    # list_filter = ('name',)

    def get_queryset(self, request):
        MPs_ids = PersonMembership.objects.filter(role='voter').values_list('member', flat=True)
        qs = Person.objects.filter(id__in=MPs_ids)
        if request.user.is_superuser:
            return qs

class LawAdmin(admin.ModelAdmin):
    list_display = ('text', 'session', 'status', 'epa')
    list_filter = ('session',)
    search_fields = ['text']


class AgendaItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'session',)
    list_filter = ('name', 'session')
    search_fields = ['name']


admin.site.register(ParliamentMember, MPAdmin)
admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Vote, VoteAdmin)
#admin.site.register(Area, LeafletGeoAdmin)
admin.site.register(Link)
admin.site.register(Ballot)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AgendaItem, AgendaItemAdmin)
admin.site.register(Law, LawAdmin)
admin.site.register(OrganizationMembership)
admin.site.register(Mandate, MandateAdmin)
