from django.contrib import admin

from parladata.admin.filters import (
    SessionListFilter,
    PersonAuthorsListFilter,
    OrganizationAuthorsListFilter,
)
from parladata.models.question import Question, Answer
from parladata.admin.link import LinkQuestionInline, LinkAnswerInline


class AnswerInline(admin.TabularInline):
    model = Answer
    autocomplete_fields = ["person_authors", "organization_authors"]
    fk_name = "question"
    exclude = []
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["title", "timestamp"]
    autocomplete_fields = [
        "person_authors",
        "organization_authors",
        "recipient_people",
        "recipient_organizations",
        "session",
    ]
    search_fields = ["title"]
    inlines = [
        LinkQuestionInline,
        AnswerInline,
    ]
    list_filter = (
        "type_of_question",
        SessionListFilter,
        PersonAuthorsListFilter,
        OrganizationAuthorsListFilter,
    )
    fields = [
        "title",
        "mandate",
        "session",
        "person_authors",
        "organization_authors",
        "recipient_people",
        "recipient_organizations",
        "recipient_text",
        "type_of_question",
        "timestamp",
        "answer_timestamp",
        "gov_id",
    ]
    readonly_fields = ["created_at", "updated_at"]


class AnswerAdmin(admin.ModelAdmin):
    list_display = ["question", "timestamp"]
    autocomplete_fields = ["question", "person_authors", "organization_authors"]
    search_fields = ["title"]
    inlines = [LinkAnswerInline]
    fields = [
        "content",
        "question",
        "person_authors",
        "organization_authors",
        "timestamp",
    ]
    readonly_fields = ["created_at", "updated_at"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
