from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple, AutocompleteSelect
from django.contrib import admin
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput

from parladata.models import Person, Question

class PersonAutocompleteSelectMultiple(AutocompleteSelectMultiple):
    def get_url(self):
        model = Question
        return reverse(self.url_name % ('admin'))


class UsersChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Person.objects.all()
        if widget is None:
            widget = PersonAutocompleteSelectMultiple(Question._meta.get_field('authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)


class PersonAutocompleteSelect(AutocompleteSelect):
    def get_url(self):
        model = Question
        return reverse(self.url_name % ('admin'))


class UserChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Person.objects.all()
        if widget is None:
            widget = PersonAutocompleteSelect(Question._meta.get_field('authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)


class MergePeopleForm(forms.Form):
    confirmed = forms.BooleanField(widget=HiddenInput())
    real_person = UserChoiceField()
    people = UsersChoiceField()
