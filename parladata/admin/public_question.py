from django.contrib import admin


from parladata.models.public_question import PublicPersonQuestion, PublicPersonAnswer



class PublicPersonQuestionAdmin(admin.ModelAdmin):
    list_display = ['recipient_person', 'created_at', 'approved_at', 'rejected_at']
    autocomplete_fields = ['recipient_person']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['recipient_person__personname__value', 'text']


class PublicPersonAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_at', 'approved_at', 'rejected_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['question']


admin.site.register(PublicPersonQuestion, PublicPersonQuestionAdmin)
admin.site.register(PublicPersonAnswer, PublicPersonAnswerAdmin)
