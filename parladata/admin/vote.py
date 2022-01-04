from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext as _

from parladata.models import Vote, Ballot

from collections import Counter

@admin.action(description='Clone vote with ballots')
def clone_vote(modeladmin, request, queryset):
    if queryset.count() == 1:
        vote = queryset.first()
        ballots = vote.ballots.all()
        new_vote = Vote()
        new_vote.save()
        for ballot in ballots:
            ballot.id = None
            ballot.vote = new_vote
            ballot.save()
    else:
        modeladmin.message_user(request, 'You can only clone one vote at a time.', messages.ERROR)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', 'get_for', 'get_against', 'get_abstain', 'get_abesnt', 'needs_editing', 'add_ballots')
    # set order of fields in the dashboard
    fields = ['name', 'timestamp', 'motion', 'result', 'needs_editing', 'tags', 'get_session', 'get_statistics', 'edit_ballots', 'get_vote_pdf']
    readonly_fields = ['get_session', 'get_statistics', 'edit_ballots', 'get_vote_pdf']

    list_filter = ('tags',)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ['name']

    actions = [clone_vote]

    autocomplete_fields = ('motion',)

    def the_tags(self, obj):
        return "%s" % (list(obj.tags.values_list('name', flat=True)), )

    def get_session(self, obj):
        return obj.motion.session.name if obj.motion and obj.motion.session else ''

    def add_ballots(self, obj):
        partial_url = '/admin/parladata/vote/addballots/'
        url = f'{settings.BASE_URL}{partial_url}?vote_id={obj.id}'
        if not obj.ballots.all():
            return mark_safe(f'<a href="{url}"><input type="button" value="Add ballots" /></a>')
        else:
            return ''

    def edit_ballots(self, obj):
        change_url = reverse('admin:parladata_ballot_changelist')
        return mark_safe(f'<a href="{change_url}?vote__id__exact={obj.id}" target="_blank"><input type="button" value="Edit ballots" /></a>')


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
            return mark_safe(f'<a href="{vote_pdf}" target="_blank"><input type="button" value="Vote pdf" /></a>')
        else:
            return ''

    def get_statistics(self, obj):
        for_votes = self.get_for(obj)
        against = self.get_against(obj)
        abstain = self.get_abstain(obj)
        abesnt = self.get_abesnt(obj)

        return mark_safe(
            f'''<table>
                <tr>
                    <th>{_("for")}</th>
                    <th>{_("against")}</th>
                    <th>{_("abstain")}</th>
                    <th>{_("absent")}</th>
                    <th>{_("all")}</th>
                </tr>
                <tr>
                    <td>{for_votes}</td>
                    <td>{against}</td>
                    <td>{abstain}</td>
                    <td>{abesnt}</td>
                    <td>{for_votes + against + abstain + abesnt}</td>
                </tr>
            </table>
            '''
            )

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
    get_statistics.allow_tags = True
    get_statistics.short_description = 'Statistics'
    get_session.short_description = 'Session'



admin.site.register(Vote, VoteAdmin)
