from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from dal import autocomplete

# Register your models here.
from .models import *
from forms import MembershipForm

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
    inlines = [
        SourcePostInline,
    ]

class MembershipAdmin(admin.ModelAdmin):
    form = MembershipForm
    inlines = [
        SourceMembershipInline,
        LinkMembershipInline,
    ]
    list_filter = ('post__role', 'organization')
    search_fields = ['person__name', 'post__role', 'organization__name']

class SessionAdmin(admin.ModelAdmin):
    inlines = [
        MilestoneSessionInline,
        SpeechSessionInline,
        MotionSessionInline,
    ]

class SpeechAdmin(admin.ModelAdmin):
    inlines = [
        MilestoneSpeechInline,
    ]

class MotionAdmin(admin.ModelAdmin):
    inlines = [
        LinkMotionInline,
    ]
class VoteAdmin(admin.ModelAdmin):
    inlines = [
        CountVoteInline,
    ]

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

class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
