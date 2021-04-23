from django.contrib import admin
from collections import Counter
from django.urls import reverse
from .models import *
from django.conf import settings
from django.db.models import Q


class LinkPersonInline(admin.TabularInline):
    model = Link
    fk_name = 'person'
    exclude = ['organization', 'membership', 'motion', 'session', 'question']
    extra = 0


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


class CountVoteInline(admin.TabularInline):
    model = Count
    fk_name = 'vote'
    extra = 0


class SpeechSessionInline(admin.TabularInline):
    model = Speech
    fk_name = 'session'
    extra = 0


class MotionSessionInline(admin.TabularInline):
    model = Motion
    fk_name = 'session'
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    #form = PersonForm
    inlines = [
        LinkPersonInline,
    ]
    list_display = ('name',)
    list_filter = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        # LinkOrganizationInline,
    ]
    autocomplete_fields = ['parent']
    search_fields = ['_name']


class MembershipAdmin(admin.ModelAdmin):
    inlines = [
        LinkMembershipInline,
    ]
    list_filter = ['organization']
    search_fields = ['person__name', 'organization___name']


class SessionAdmin(admin.ModelAdmin):
    inlines = [
        SpeechSessionInline,
        MotionSessionInline,
    ]
    search_fields = ['name']


class SpeechAdmin(admin.ModelAdmin):
    #form = SpeechForm
    search_fields = ['speaker__name', 'content']
    inlines = [
    ]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        LinkQuestionInline
    ]


class MotionAdmin(admin.ModelAdmin):
    #form = MotionForm
    list_display = ('id',
                    'text',
                    'date',
                    'epa',
                    'result',
                    'requirement',
                    'get_for',
                    'get_against',
                    'get_abstain',
                    'get_not',
                    'link_to_vote')

    list_editable = ('result',)
    list_filter = ('result', 'date', 'session')
    search_fields = ['text']
    inlines = [
        LinkMotionInline,
    ]

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
        link = reverse("admin:parladata_vote_change", args=[Vote.objects.get(motion=obj).id])
        return u'<a href="%s">Vote</a>' % (link)

    link_to_vote.allow_tags = True

    get_for.short_description = 'for'
    get_against.short_description = 'against'
    get_abstain.short_description = 'abstain'
    get_not.short_description = 'absent'


class VoteAdmin(admin.ModelAdmin):
    #form = VoteForm
    list_display = ('id', 'name', 'the_tags', )

    list_filter = ('tags',)
    inlines = [
        CountVoteInline,
    ]
    search_fields = ['name']

    def the_tags(self, obj):
        return "%s" % (obj.tags.all(), )
    the_tags.short_description = 'tags'


class ContactAdmin(admin.ModelAdmin):
    #form = ContactForm
    list_display = ('id', 'value')

    search_fields = ['value']


# class PersonAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Person.objects.none()

#         qs = Person.objects.all()

#         if self.q:
#             qs = qs.filter(name__icontains=self.q)

#         return qs


# class PostAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Post.objects.none()

#         qs = Post.objects.all()

#         if self.q:
#             qs = qs.filter(organization__name__icontains=self.q)

#         return qs


# class MembershipAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Membership.objects.none()

#         qs = Membership.objects.all()

#         if self.q:
#             qs = qs.filter(person__name__icontains=self.q)

#         return qs


# class OrganizationAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Organization.objects.none()

#         qs = Organization.objects.all()

#         if self.q:
#             qs = qs.filter(Q(_name__icontains=self.q) | Q(_acronym__icontains=self.q))

#         return qs


# class LinkAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Link.objects.none()

#         qs = Link.objects.all()

#         if self.q:
#             qs = qs.filter(url__icontains=self.q)

#         return qs


# class AreaAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Area.objects.none()

#         qs = Area.objects.all()

#         if self.q:
#             qs = qs.filter(name__icontains=self.q)

#         return qs


# class SessionAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Session.objects.none()

#         qs = Session.objects.all()

#         if self.q:
#             qs = qs.filter(name__icontains=self.q)

#         return qs


# class MotionAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Motion.objects.none()

#         qs = Motion.objects.all()

#         if self.q:
#             qs = qs.filter(text__icontains=self.q)

#         return qs


class PersonEducation(Person):
    class Meta:
        proxy = True

class PersonEducationAdmin(admin.ModelAdmin):
    #form = PersonForm
    list_display = ['name', 'education', 'number_of_mandates', 'education_level']
    search_fields = ['name', 'number_of_mandates']
    list_filter = ['education', 'number_of_mandates']
    fields = ('name', 'education', 'education_level')


class ParliamentMember(Person):
    class Meta:
        proxy = True


class MPAdmin(admin.ModelAdmin):
    #form = PersonForm
    list_display = ('name',)
    list_filter = ('name',)

    def get_queryset(self, request):
        MPs_ids = Membership.objects.filter(role='voter').values_list('person', flat=True)
        qs = Person.objects.filter(id__in=MPs_ids)
        if request.user.is_superuser:
            return qs

class LawAdmin(admin.ModelAdmin):
    list_display = ('text', 'session', 'status', 'epa', 'classification', 'procedure_ended')
    list_filter = ('session',)
    search_fields = ['text']

admin.site.register(Person, PersonAdmin)
admin.site.register(PersonEducation, PersonEducationAdmin)
admin.site.register(ParliamentMember, MPAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(PersonMembership, MembershipAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Vote, VoteAdmin)
#admin.site.register(Area, LeafletGeoAdmin)
admin.site.register(Link)
admin.site.register(Ballot)
admin.site.register(Question, QuestionAdmin)
admin.site.register(OrganizationName)
admin.site.register(AgendaItem)
admin.site.register(Law, LawAdmin)
admin.site.register(OrganizationMembership)
