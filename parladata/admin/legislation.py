from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse

from parladata.models import Law, Procedure, ProcedurePhase, LegislationConsideration, LegislationStatus


class LawAdmin(admin.ModelAdmin):
    list_display = ('text', 'session', 'status', 'epa')
    list_filter = ('session',)
    search_fields = ('text',)


class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)


class ProcedurePhaseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class LegislationConsiderationAdmin(admin.ModelAdmin):
    list_display = ('legislation', 'procedure_phase', 'timestamp')
    autocomplete_fields = ('legislation', 'organization')


class LegislationStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Law, LawAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(ProcedurePhase, ProcedurePhaseAdmin)
admin.site.register(LegislationConsideration, LegislationConsiderationAdmin)
admin.site.register(LegislationStatus, LegislationStatusAdmin)
