from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

from parladata.models import Vote

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'the_tags', 'add_ballots')

    list_filter = ('tags',)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ['name']

    def the_tags(self, obj):
        return "%s" % (obj.tags.all(), )
    the_tags.short_description = 'tags'

    def add_ballots(self, obj):
        partial_url = '/admin/parladata/vote/addballots/'
        url = f'{settings.BASE_URL}{partial_url}?vote_id={obj.id}'
        if not obj.ballots.all():
            return mark_safe(f'<a href="{url}"><input type="button" value="Add ballots" /></a>')
        else:
            return ''

    add_ballots.allow_tags = True
    add_ballots.short_description = 'Add ballots'


admin.site.register(Vote, VoteAdmin)
