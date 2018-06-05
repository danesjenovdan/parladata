from dal import autocomplete
from django import forms
from .models import Membership, Post, Speech, Person
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
import admin


class MembershipForm(forms.ModelForm):
    """Form for debuging memberships."""
    class Meta:
        model = Membership
        fields = ('__all__')
        widgets = {
            'person': autocomplete.ModelSelect2(url='API:person-autocomplete'),
            'organization': autocomplete.ModelSelect2(url='API:organization-autocomplete'), 
        }

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super(MembershipForm, self).save(commit=False)
        return instance

def add_related_field_wrapper(form, col_name):
    rel_model = form.Meta.model
    rel = rel_model._meta.get_field(col_name).rel
    form.fields[col_name].widget = RelatedFieldWidgetWrapper(form.fields[col_name].widget, rel, admin.site, can_add_related=True, can_change_related=True)


class PostForm(forms.ModelForm):
    """Form for posts."""

    class Meta:
        model = Post
        fields = ('__all__')
        widgets = {
            'membership': autocomplete.ModelSelect2(url='API:membership-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # add_related_field_wrapper(self, 'post')

    def save(self, *args, **kwargs):
        instance = super(PostForm, self).save(commit=False)
        return instance


class SpeechForm(forms.ModelForm):
    """Form for speechs."""

    class Meta:
        model = Speech
        fields = ('__all__')
        widgets = {
            'speaker': autocomplete.ModelSelect2(url='API:person-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(SpeechForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super(SpeechForm, self).save(commit=False)
        return instance


class PersonForm(forms.ModelForm):
    """Form for person."""
    class Meta:
        model = Person
        fields = ('__all__')
        widgets = {
            'gov_url': autocomplete.ModelSelect2(url='API:link-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super(PersonForm, self).save(commit=False)
        return instance