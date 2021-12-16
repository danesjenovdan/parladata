from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

from parladata.models import Vote, Ballot

from collections import Counter

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', 'get_for', 'get_against', 'get_abstain', 'get_abesnt', 'needs_editing', 'add_ballots', 'edit_ballots')
    # set order of fields in the dashboard
    fields = ['name', 'timestamp', 'motion', 'result', 'needs_editing', 'tags', 'edit_ballots', 'get_vote_pdf']
    readonly_fields = ['edit_ballots', 'get_vote_pdf']

    list_filter = ('tags',)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ['name']

    autocomplete_fields = ('motion',)

    def the_tags(self, obj):
        return "%s" % (list(obj.tags.values_list('name', flat=True)), )

    def add_ballots(self, obj):
        partial_url = '/admin/parladata/vote/addballots/'
        url = f'{settings.BASE_URL}{partial_url}?vote_id={obj.id}'
        if not obj.ballots.all():
            return mark_safe(f'<a href="{url}"><input type="button" value="Add ballots" /></a>')
        else:
            return ''

    def edit_ballots(self, obj):
        change_url = reverse('admin:parladata_ballot_changelist')
        if obj.needs_editing:
            return mark_safe(f'<a href="{change_url}?vote__id__exact={obj.id}"><input type="button" value="Edit ballots" /></a>')
        else:
            return ''

    def get_for(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote=obj).values_list("option", flat=True))).get("for", 0)
        return results

    def get_against(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote=obj).values_list("option", flat=True))).get("against", 0)
        return results

    def get_abstain(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote=obj).values_list("option", flat=True))).get("abstain", 0)
        return results

    def get_abesnt(self, obj):
        results = dict(Counter(Ballot.objects.filter(vote=obj).values_list("option", flat=True))).get("absent", 0)
        return results

    def get_vote_pdf(self, obj):
        vote_pdf = obj.motion.links.filter(tags__name='vote-pdf').values_list('url', flat=True).first()
        if vote_pdf:
            return mark_safe(f'<a href="{vote_pdf}"><input type="button" value="Vote pdf" /></a>')
        else:
            return ''

    get_for.short_description = 'for'
    get_against.short_description = 'against'
    get_abstain.short_description = 'abstain'
    get_abesnt.short_description = 'absent'
    the_tags.short_description = 'tags'
    add_ballots.allow_tags = True
    add_ballots.short_description = 'Add ballots'
    edit_ballots.allow_tags = True
    edit_ballots.short_description = 'Edit ballots'

    get_vote_pdf.allow_tags = True
    get_vote_pdf.short_description = 'Vote pdf'



admin.site.register(Vote, VoteAdmin)
