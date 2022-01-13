from django.contrib import admin

from import_export.resources import ModelResource
from import_export.admin import ExportMixin
from import_export.fields import Field

from parlacards.models import PersonNumberOfSpokenWords

from parlacards.admin.common import LatestScoresAdmin


class PersonNumberOfSpokenWordsResource(ModelResource):
    name = Field()

    class Meta:
        model = PersonNumberOfSpokenWords
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.person.name


# TODO this could be abstracted away into a sort of current score admin
class PersonNumberOfSpokenWordsAdmin(ExportMixin, LatestScoresAdmin):
    resource_class = PersonNumberOfSpokenWordsResource


admin.site.register(PersonNumberOfSpokenWords, PersonNumberOfSpokenWordsAdmin)
