from django import forms
from .models import Plot
from django.utils.translation import gettext_lazy as _


class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = ['name', 'area', 'soil_type', 'irrigation_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        self.fields['name'].label = _('Name')
        self.fields['area'].label = _('Area')
        self.fields['soil_type'].label = _('Soil type')
        self.fields['irrigation_type'].label = _('Irrigation')
        self.fields['name'].widget.attrs['placeholder'] = _('Field name')
        self.fields['area'].widget.attrs['placeholder'] = _('Enter area in acres')
        self.fields['soil_type'].widget.attrs['placeholder'] = _('For example, black soil')
        self.fields['irrigation_type'].widget.attrs['placeholder'] = _('For example, drip or canal')
