from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from dal import autocomplete
from collections import Counter
from django.core.urlresolvers import reverse
from .models import *
from forms import MembershipForm, PostForm, SpeechForm


class OtherNamePersonInline(admin.TabularInline):
    model = OtherName
    fk_name = 'person'
    exclude = ['organization']
    extra = 0


class OtherNameOrganizationInline(admin.TabularInline):
    model = OtherName
    fk_name = 'organization'
    exclude = ['person']
    extra = 0


class LinkPersonInline(admin.TabularInline):
    model = Link
    fk_name = 'person'
    exclude = ['organization', 'membership', 'motion']
    extra = 0


class LinkOrganizationInline(admin.TabularInline):
    model = Link
    fk_name = 'organization'
    exclude = ['person', 'membership', 'motion']
    extra = 0


class LinkMembershipInline(admin.TabularInline):
    model = Link
    fk_name = 'membership'
    exclude = ['person', 'organization', 'motion']
    extra = 0


class LinkMotionInline(admin.TabularInline):
    model = Link
    fk_name = 'motion'
    exclude = ['person', 'membership', 'organization']
    extra = 0


class LinkQuestionInline(admin.TabularInline):
    model = Link
    fk_name = 'question'
    exclude = []
    extra = 0


class IdentifierPersonInline(admin.TabularInline):
    model = Identifier
    fk_name = 'person'
    exclude = ['organization']
    extra = 0


class IdentifierOrganizationInline(admin.TabularInline):
    model = Identifier
    fk_name = 'organization'
    exclude = ['person']
    extra = 0


class SourcePersonInline(admin.TabularInline):
    model = Source
    fk_name = 'person'
    exclude = ['organization', 'membership', 'post', 'contact_detail']
    extra = 0


class SourceOrganizationInline(admin.TabularInline):
    model = Source
    fk_name = 'organization'
    exclude = ['person', 'membership', 'post', 'contact_detail']
    extra = 0


class SourceMembershipInline(admin.TabularInline):
    model = Source
    fk_name = 'membership'
    exclude = ['organization', 'person', 'post', 'contact_detail']
    extra = 0


class SourcePostInline(admin.TabularInline):
    model = Source
    fk_name = 'post'
    exclude = ['organization', 'membership', 'person', 'contact_detail']
    extra = 0


class SourceContactDetailInline(admin.TabularInline):
    model = Source
    fk_name = 'contact_detail'
    exclude = ['organization', 'membership', 'post', 'person']
    extra = 0


class MilestoneMandateInline(admin.TabularInline):
    model = Milestone
    fk_name = 'mandate'
    exclude = ['organization', 'session', 'speech', 'person']
    extra = 0


class MilestoneOrganizationInline(admin.TabularInline):
    model = Milestone
    fk_name = 'organization'
    exclude = ['mandate', 'session', 'speech', 'person']
    extra = 0


class MilestoneSessionInline(admin.TabularInline):
    model = Milestone
    fk_name = 'session'
    exclude = ['organization', 'mandate', 'speech', 'person']
    extra = 0


class MilestoneSpeechInline(admin.TabularInline):
    model = Milestone
    fk_name = 'speech'
    exclude = ['organization', 'session', 'mandate', 'person']
    extra = 0


class MilestonePersonInline(admin.TabularInline):
    model = Milestone
    fk_name = 'person'
    exclude = ['organization', 'session', 'speech', 'mandate']
    extra = 0


class CountVoteInline(admin.TabularInline):
    model = Count
    fk_name = 'vote'
    extra = 0


class ContactDetailsPersonInline(admin.TabularInline):
    model = ContactDetail
    fk_name = 'person'
    exclude = ['organization', 'post', 'membership']
    extra = 0


class ContactDetailsOrganizationInline(admin.TabularInline):
    model = ContactDetail
    fk_name = 'organization'
    exclude = ['person', 'post', 'membership']
    extra = 0


class ContactDetailsPostInline(admin.TabularInline):
    model = ContactDetail
    fk_name = 'post'
    exclude = ['organization', 'person', 'membership']
    extra = 0


class ContactDetailsMembershipInline(admin.TabularInline):
    model = ContactDetail
    fk_name = 'membership'
    exclude = ['organization', 'post', 'person']
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
    inlines = [
        OtherNamePersonInline,
        ContactDetailsPersonInline,
        LinkPersonInline,
        IdentifierPersonInline,
        SourcePersonInline,
        MilestonePersonInline,
    ]
    list_display = ('name', 'gov_image')
    list_filter = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        OtherNameOrganizationInline,
        ContactDetailsOrganizationInline,
        LinkOrganizationInline,
        IdentifierOrganizationInline,
        SourceOrganizationInline,
        MilestoneOrganizationInline,
    ]


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    inlines = [
        SourcePostInline,
    ]
    search_fields = ['membership__person__name',
                     'membership__organization__name']


class MembershipAdmin(admin.ModelAdmin):
    form = MembershipForm
    inlines = [
        SourceMembershipInline,
        LinkMembershipInline,
    ]
    list_filter = ['organization']
    search_fields = ['person__name', 'organization__name']


class SessionAdmin(admin.ModelAdmin):
    inlines = [
        MilestoneSessionInline,
        SpeechSessionInline,
        MotionSessionInline,
    ]
    search_fields = ['name']


class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    inlines = [
        MilestoneSpeechInline,
    ]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        LinkQuestionInline
    ]


class MotionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'text',
                    'date',
                    'result',
                    'requirement',
                    'get_for',
                    'get_against',
                    'get_abstain',
                    'get_not',
                    'link_to_vote')

    list_editable = ('result',)
    list_filter = ('result', 'date')
    search_fields = ['text']
    inlines = [
        LinkMotionInline,
    ]

    def get_for(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("za", 0)
        return results

    def get_against(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("proti", 0)
        return results

    def get_abstain(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("kvorum", 0)
        return results

    def get_not(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True))).get("ni", 0)
        return results

    def link_to_vote(self, obj):
        link = reverse("admin:parladata_vote_change", args=[Vote.objects.get(motion=obj).id])
        return u'<a href="%s">Vote</a>' % (link)

    link_to_vote.allow_tags = True

    get_for.short_description = 'Za'
    get_against.short_description = 'Proti'
    get_abstain.short_description = 'Vzdrazan'
    get_not.short_description = 'Ni'


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', )

    list_filter = ('tags',)
    inlines = [
        CountVoteInline,
    ]
    search_fields = ['name']

    def the_tags(self, obj):
        return "%s" % (obj.tags.all(), )
    the_tags.short_description = 'tags'


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PostAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Post.objects.none()

        qs = Post.objects.all()

        if self.q:
            qs = qs.filter(organization__name__icontains=self.q)

        return qs


class MembershipAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Membership.objects.none()

        qs = Membership.objects.all()

        if self.q:
            qs = qs.filter(person__name__icontains=self.q)

        return qs


admin.site.register(Person, PersonAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Speech, SpeechAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Area, LeafletGeoAdmin)
admin.site.register(Link)
admin.site.register(Ballot)
admin.site.register(Question, QuestionAdmin)
