from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import Q
from django.urls import reverse

from parladata.models import *
from parladata.models.task import Task
from parladata.models.versionable_properties import *
from parladata.models.common import *
from parladata.admin.link import LinkMotionInline
from parladata.admin.filters import SessionListFilter

from collections import Counter


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
        'created_at',
        'tag_list',
    )
    autocomplete_fields = ('session', 'champions', 'agenda_items', 'law')

    list_editable = ('result',)
    list_filter = (SessionListFilter, 'result', 'datetime',)
    search_fields = ['text', 'title']
    inlines = [
        LinkMotionInline,
    ]
    list_per_page = 25
    readonly_fields = ['created_at', 'updated_at']

    # set order of fields in the dashboard
    fields = ['title', 'session', 'datetime', 'result', 'agenda_items', 'law', 'champions', 'summary', 'text', 'classification', 'requirement', 'parser_names', 'tags']

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

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


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

admin.site.register(Motion, MotionAdmin)
