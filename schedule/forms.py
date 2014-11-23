from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

class ProspectiveAdminField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        if not value:
            return self.queryset.none()
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'], code='list')
        models = []
        id_values = []
        for val in value:
            if "@" in val:
                try:
                    model, created = self.queryset.get_or_create(email=val)
                except ValueError:
                    return ValidationError(
                            "Invalid email address",
                            code='invalid_email',
                            params={"pk": val})
                models.append(model)
            else:
                try:
                    self.queryset.filter(pk=val)
                except ValueError:
                    raise ValidationError(
                        self.error_messages['invalid_pk_value'],
                        code='invalid_pk_value',
                        params={'pk': val},
                    )
                id_values.append(val)
        qs = list(self.queryset.filter(pk__in=id_values))
        pks = set(str(o.pk) for o in qs)
        for val in id_values:
            if str(val) not in pks:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )
        self.run_validators(value)
        return qs + models

class CreateConferenceForm(forms.ModelForm):
    admins = forms.ModelMultipleChoiceField(User.objects.all(),
            widget=forms.MultipleHiddenInput)
    prospective_admins = ProspectiveAdminField(ProspectiveAdmin.objects.all(),
            widget=forms.MultipleHiddenInput)

    class Meta:
        model = Conference
        fields = ['name', 'public', 'admins', 'prospective_admins']

class UpdateConferenceForm(CreateConferenceForm):
    class Meta(CreateConferenceForm.Meta):
        fields = ['name', 'public', 'admins', 'prospective_admins', 'archived']

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name']

class RoleTypeForm(forms.ModelForm):
    class Meta:
        model = RoleType
        fields = ['role']
