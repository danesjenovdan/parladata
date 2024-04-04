from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from parladata.models import *
from parladata.models.task import Task
from parladata.models.versionable_properties import *
from parladata.models.common import *
from parladata.admin.filters import ParsableFilter

from parladata.admin.link import *


class MandateAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "beginning",
    )
    list_filter = (
        "description",
        "beginning",
    )
    search_fields = (
        "description",
        "beginning",
    )


class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "file_url"]
    list_filter = ()

    readonly_fields = ["created_at", "updated_at"]
    list_filter = (ParsableFilter,)

    def file_url(self, obj):
        return obj.file.url


class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "value")
    search_fields = ["value"]
    readonly_fields = ["created_at", "updated_at"]


class EducationLevelAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ("order",)
    list_display = ("id", "text")
    search_fields = ["text"]
    readonly_fields = ["created_at", "updated_at"]


class BallotAdmin(admin.ModelAdmin):
    list_display = ["__str__", "option", "vote"]
    autocomplete_fields = ["personvoter", "orgvoter", "vote"]
    list_filter = ("vote",)
    list_editable = ["option"]
    readonly_fields = ["created_at", "updated_at"]


class AreaAdmin(admin.ModelAdmin):
    list_display = ["name", "identifier", "parent", "classification"]
    search_fields = ["name"]


admin.site.site_header = "Parladata"
admin.site.register(Task)
admin.site.register(Area, AreaAdmin)
admin.site.register(Ballot, BallotAdmin)

admin.site.register(Mandate, MandateAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
