from django.contrib import admin

from parladata.admin.filters import SessionListFilter, PersonAuthorsListFilter, OrganizationAuthorsListFilter
from parladata.models.question import Question
from parladata.admin.link import LinkQuestionInline


class QuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'session']
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline
    ]
    list_filter = ('type_of_question', SessionListFilter, PersonAuthorsListFilter, OrganizationAuthorsListFilter)
    fields = ['title', 'session', 'person_authors', 'organization_authors', 'recipient_people', 'recipient_organizations', 'recipient_text', 'type_of_question', 'timestamp', 'answer_timestamp', 'gov_id']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Question, QuestionAdmin)
