from django.contrib import admin
from django import forms
from django.db import models

from parladata.models.speech import Speech
from parladata.models.motion import Motion

from parladata.admin.filters import SessionListFilter

@admin.action(description='Duplicate selected speeches')
def duplicate_speech(modeladmin, request, queryset):
    for speech in queryset:
        # first, move all consecutive speeches forward for one order
        # TODO this is a bit inefficient, maybe problematic for LONG sessions
        speeches_to_move = Speech.objects.filter(
            session=speech.session,
            order__gt=speech.order,
        )
        for speech_to_move in speeches_to_move:
            speech_to_move.order += 1
            speech_to_move.save()

        # clear lemmatized_content for the speech
        speech.lemmatized_content = None
        speech.save()

        # make a copy of the speech and increment its order
        speech.pk = None
        speech.order += 1
        speech.save()

class SpeechForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motions'].queryset = Motion.objects.filter(
            session=self.instance.session)

class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    fields = ['session', 'content', 'speaker', 'order', 'motions', 'start_time', 'tags', 'lemmatized_content']
    list_filter = (SessionListFilter, 'tags')
    search_fields = ['speaker__personname__value', 'content']
    autocomplete_fields = ['motions', 'speaker', 'session']
    inlines = []
    list_display = ('id',
                    'order',
                    'tag_list',
                    'session_name',
                    'speaker',)
    ordering = ('order',)
    list_per_page = 25
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple()},
    }
    actions = [duplicate_speech]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags', 'session', 'speaker')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def session_name(self, obj):
        return obj.session.name

admin.site.register(Speech, SpeechAdmin)
