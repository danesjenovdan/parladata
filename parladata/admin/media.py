from django.contrib import admin
from django.db import models

from parladata.models import Medium, MediaReport


# class MediaReportInline(admin.TabularInline):
#     model = MediaReport
#     fk_name = 'medium'
#     # exclude = ['person', 'organization', 'motion', 'session', 'membership', 'question']
#     extra = 0


class MediumAdmin(admin.ModelAdmin):
    # inlines = (MediaReportInline,)
    list_display = ('name', 'url', 'active',)
    search_fields = ('name', 'url',)
    list_filter = ('active',)
    readonly_fields = ['created_at', 'updated_at']


class MediaReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'medium',)
    search_fields = ('title',)
    list_filter = ('medium__name', 'report_date')
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Medium, MediumAdmin)
admin.site.register(MediaReport, MediaReportAdmin)
