from django import forms

from schedule.models import *

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ['conference']

class OtherCommitmentForm(forms.ModelForm):
    class Meta:
        model = OtherCommitment

#OtherCommitmentFormset = forms.inlineformset_factory(AvailabilityForm, OtherCommitmentForm, extra=2)
