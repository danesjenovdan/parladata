from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple, AutocompleteSelect
from django.contrib import admin
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

from parladata.models import Person, Question, Organization

from datetime import datetime

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
    people_did_not_vote = UsersChoiceField(required=False)


class AddAnonymousBallotsForm(forms.Form):
    edit = forms.BooleanField(widget=HiddenInput())
    people_for = forms.IntegerField(required=True, initial=0)
    people_against = forms.IntegerField(required=True, initial=0)
    people_abstain = forms.IntegerField(required=True, initial=0)
    people_absent = forms.IntegerField(required=True, initial=0)
    people_did_not_vote = forms.IntegerField(required=True, initial=0)


class VersionableValidatorInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        dates = []
        for form in self.forms:
            valid_from = form.cleaned_data.get('valid_from', datetime.min)
            valid_to = form.cleaned_data.get('valid_to', datetime.min)
            if not valid_from:
                valid_from = datetime.min

            if not valid_to:
                valid_to = datetime.max

            for date in dates:
                print((date[1] - valid_from).total_seconds(), (date[0] - valid_to).total_seconds())
                if (date[1] - valid_from).total_seconds() * (date[0] - valid_to).total_seconds() <= 0:
                    raise forms.ValidationError(_('Time intervals are in intersection'))
            dates.append((valid_from, valid_to))
