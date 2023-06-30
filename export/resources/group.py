from export.resources.common import CardExport, get_cached_group_name, get_cached_person_name
from import_export.fields import Field

from parlacards.models import (
    GroupDiscord,
    GroupVocabularySize,
    GroupNumberOfQuestions,
    GroupMonthlyVoteAttendance,
    GroupVoteAttendance,
    GroupTfidf,
    GroupVotingDistance

)



class GroupCardExport(CardExport):
    name = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(group_id=request_id).order_by('-timestamp')

    def dehydrate_name(self, score):
        return get_cached_group_name(score.group_id)

    class Meta:
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)

class GroupDiscordResource(GroupCardExport):
    class Meta:
        model = GroupDiscord


class GroupVocabularySizeResource(GroupCardExport):
    class Meta:
        model = GroupVocabularySize


class GroupNumberOfQuestionsResource(GroupCardExport):
    class Meta:
        model = GroupNumberOfQuestions


class GroupMonthlyVoteAttendanceResource(GroupCardExport):
    class Meta:
        model = GroupMonthlyVoteAttendance


class GroupVoteAttendanceResource(GroupCardExport):
    class Meta:
        model = GroupVoteAttendance


class GroupVotesInCommonResource(GroupCardExport):
    target_person = Field()

    def dehydrate_target_person(self, score):
        return get_cached_person_name(score.target_id)
    class Meta:
        model = GroupVotingDistance
        fields = ('name', 'target_person', 'value', 'timestamp',)
        export_order = ('name', 'target_person', 'value', 'timestamp',)


class GroupTfidfResource(GroupCardExport):
    class Meta:
        model = GroupTfidf
        fields = ('name', 'token', 'value', 'timestamp',)
        export_order = ('name', 'token', 'value', 'timestamp',)
