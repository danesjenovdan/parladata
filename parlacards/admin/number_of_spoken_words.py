from django.contrib import admin

from import_export.admin import ExportMixin

from export.resources.person import PersonNumberOfSpokenWordsResource

from parlacards.models import PersonNumberOfSpokenWords
from parlacards.admin.common import LatestScoresAdmin


# TODO this could be abstracted away into a sort of current score admin
class PersonNumberOfSpokenWordsAdmin(ExportMixin, LatestScoresAdmin):
    resource_class = PersonNumberOfSpokenWordsResource


admin.site.register(PersonNumberOfSpokenWords, PersonNumberOfSpokenWordsAdmin)
