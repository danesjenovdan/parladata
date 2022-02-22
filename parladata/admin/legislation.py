from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse

from parladata.models import Law, Procedure, ProcedurePhase, LegislationConsideration, LegislationStatus, LegislationClassification
from parladata.admin.filters import SessionListFilter


class LawAdmin(admin.ModelAdmin):
    list_display = ('text', 'session', 'status', 'epa')
    list_filter = (SessionListFilter,)
    search_fields = ('text',)
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20


class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ('name',)


class ProcedurePhaseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ('procedure',)


class LegislationConsiderationAdmin(admin.ModelAdmin):
    list_display = ('legislation', 'procedure_phase', 'timestamp')
    autocomplete_fields = ('legislation', 'organization', 'session', 'procedure_phase')
    readonly_fields = ['created_at', 'updated_at']


class LegislationStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ['created_at', 'updated_at']


class LegislationClassificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Law, LawAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(ProcedurePhase, ProcedurePhaseAdmin)
admin.site.register(LegislationConsideration, LegislationConsiderationAdmin)
admin.site.register(LegislationStatus, LegislationStatusAdmin)
admin.site.register(LegislationClassification, LegislationClassificationAdmin)
