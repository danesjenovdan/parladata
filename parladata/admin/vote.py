from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

from parladata.models import Vote, Ballot

from collections import Counter

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', 'get_for', 'get_against', 'get_abstain', 'get_abesnt', 'add_ballots')

    list_filter = ('tags',)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ['name']

    def the_tags(self, obj):
        return "%s" % (list(obj.tags.values_list('name', flat=True)), )
    

    def add_ballots(self, obj):
        partial_url = '/admin/parladata/vote/addballots/'
        url = f'{settings.BASE_URL}{partial_url}?vote_id={obj.id}'
        if not obj.ballots.all():
            return mark_safe(f'<a href="{url}"><input type="button" value="Add ballots" /></a>')
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

    get_for.short_description = 'for'
    get_against.short_description = 'against'
    get_abstain.short_description = 'abstain'
    get_abesnt.short_description = 'absent'
    the_tags.short_description = 'tags'
    add_ballots.allow_tags = True
    add_ballots.short_description = 'Add ballots'


admin.site.register(Vote, VoteAdmin)
