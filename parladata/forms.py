from dal import autocomplete

from django import forms
from .models  import Membership


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('__all__')
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete')
        }