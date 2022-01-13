from django.contrib import admin

from import_export.resources import ModelResource
from import_export.admin import ExportMixin
from import_export.fields import Field

from parlacards.models import GroupDiscord

from parlacards.admin.common import LatestScoresAdmin


class GroupDiscordResource(ModelResource):
    name = Field()

    class Meta:
        model = GroupDiscord
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.group.name


class GroupDiscordAdmin(ExportMixin, LatestScoresAdmin):
    resource_class = GroupDiscordResource


admin.site.register(GroupDiscord, GroupDiscordAdmin)
