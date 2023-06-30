from export.resources.common import CardExport
from import_export.fields import Field

from parlacards.models import GroupDiscord


class GroupDiscordResource(CardExport):
    name = Field()

    class Meta:
        model = GroupDiscord
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)

    def dehydrate_name(self, score):
        return score.group.name
