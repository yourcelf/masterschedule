from django import forms
from django.forms.models import inlineformset_factory

from schedule.models import *

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name']

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ['conference']

OtherCommitmentFormset = inlineformset_factory(Person,
        OtherCommitment,
        extra=2,
        fields=['start_date', 'end_date'])
