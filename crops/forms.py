from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Crop, CropCycle

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'variety', 'typical_cycle_days', 'expected_yield_per_acre']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'variety': forms.TextInput(attrs={'class': 'form-control'}),
            'typical_cycle_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_yield_per_acre': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'name': _('Name'), 'variety': _('Variety'),
            'typical_cycle_days': _('Cycle days'),
            'expected_yield_per_acre': _('Expected yield per acre'),
        }
        for field_name, label in labels.items():
            self.fields[field_name].label = label

class CropCycleForm(forms.ModelForm):
    class Meta:
        model = CropCycle
        fields = [
            'plot', 'crop', 'season', 'sowing_date', 'expected_harvest_date', 
            'actual_harvest_date', 'growth_stage', 'expected_yield', 
            'actual_yield', 'notes'
        ]
        widgets = {
            'plot': forms.Select(attrs={'class': 'form-select'}),
            'crop': forms.Select(attrs={'class': 'form-select'}),
            'season': forms.TextInput(attrs={'class': 'form-control'}),
            'sowing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'growth_stage': forms.Select(attrs={'class': 'form-select'}),
            'expected_yield': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_yield': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show plots and crops belonging to this user
            from plots.models import Plot
            self.fields['plot'].queryset = Plot.objects.filter(farm__owner=user)
            self.fields['crop'].queryset = Crop.objects.filter(user=user)
        labels = {
            'plot': _('Field'), 'crop': _('Crop'), 'season': _('Season'),
            'sowing_date': _('Sowing date'), 'expected_harvest_date': _('Expected harvest date'),
            'actual_harvest_date': _('Actual harvest date'), 'growth_stage': _('Growth stage'),
            'expected_yield': _('Expected yield'), 'actual_yield': _('Actual yield'),
            'notes': _('Notes'),
        }
        for field_name, label in labels.items():
            self.fields[field_name].label = label

from .models import Harvest

class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = [
            'date', 'quantity', 'grade_or_quality', 'moisture_content',
            'labor_cost', 'transport_cost', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grade_or_quality': forms.TextInput(attrs={'class': 'form-control'}),
            'moisture_content': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'labor_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transport_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'date': _('Date'), 'quantity': _('Quantity'),
            'grade_or_quality': _('Grade or quality'),
            'moisture_content': _('Moisture percentage'),
            'labor_cost': _('Labour cost'), 'transport_cost': _('Transport cost'),
            'notes': _('Notes'),
        }
        for field_name, label in labels.items():
            self.fields[field_name].label = label
