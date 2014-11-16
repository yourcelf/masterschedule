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

class CreateConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['name', 'public', 'admins']

class UpdateConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['name', 'public', 'admins', 'archived']

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name']

class RoleTypeForm(forms.ModelForm):
    class Meta:
        model = RoleType
        fields = ['role']
