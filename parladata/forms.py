from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple, AutocompleteSelect
from django.contrib import admin
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput

from parladata.models import Person, Question, Organization

class QuestionAutocompleteSelectMultiple(AutocompleteSelectMultiple):
    def get_url(self):
        model = Question
        return reverse(self.url_name % ('admin'))


class QuestionAutocompleteSelect(AutocompleteSelect):
    def get_url(self):
        model = Question
        return reverse(self.url_name % ('admin'))


# person autocompelte field
class UserChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Person.objects.all()
        if widget is None:
            widget = QuestionAutocompleteSelect(Question._meta.get_field('person_authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)

# multiple select person autocompelte field
class UsersChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Person.objects.all()
        if widget is None:
            widget = QuestionAutocompleteSelectMultiple(Question._meta.get_field('person_authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)


# Organization autocompelte field
class OrganizationChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Organization.objects.all()
        if widget is None:
            widget = QuestionAutocompleteSelect(Question._meta.get_field('organization_authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)


# multiple select Organization autocompelte field
class OrganizationsChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset=None, widget=None, **kwargs):
        model = Question
        if queryset is None:
            queryset = Organization.objects.all()
        if widget is None:
            widget = QuestionAutocompleteSelectMultiple(Question._meta.get_field('organization_authors'), admin.site)
        super().__init__(queryset, widget=widget, **kwargs)


class MergePeopleForm(forms.Form):
    confirmed = forms.BooleanField(widget=HiddenInput())
    real_person = UserChoiceField()
    people = UsersChoiceField()


class MergeOrganizationsForm(forms.Form):
    confirmed = forms.BooleanField(widget=HiddenInput())
    real_organization = OrganizationChoiceField()
    organizations = OrganizationsChoiceField()


class AddBallotsForm(forms.Form):
    confirmed = forms.BooleanField(widget=HiddenInput())
    edit = forms.BooleanField(widget=HiddenInput())
    people_for = UsersChoiceField(required=False)
    people_against = UsersChoiceField(required=False)
    people_abstain = UsersChoiceField(required=False)
    people_absent = UsersChoiceField(required=False)
    people_did_not_vote = UserChoiceField(required=False)
