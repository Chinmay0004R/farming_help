from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Farm
from .models import Expense, Sale, DiaryEntry, Reminder
from django.utils.translation import gettext_lazy as _


class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'latitude', 'longitude', 'total_area']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        self.fields['name'].label = _('Name')
        self.fields['location'].label = _('Location')
        self.fields['total_area'].label = _('Total area')
        self.fields['name'].widget.attrs['placeholder'] = _('Farm name')
        self.fields['location'].widget.attrs['placeholder'] = _('Village, district, or state')
        self.fields['location'].help_text = _('Enter a place or use the button to select your current location.')
        self.fields['latitude'].label = _('Latitude')
        self.fields['longitude'].label = _('Longitude')
        self.fields['total_area'].widget.attrs['placeholder'] = _('Enter area in acres')


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['farm', 'category', 'amount', 'date', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['farm'].queryset = Farm.objects.filter(owner=user)
        self.fields['farm'].required = False
        self.fields['farm'].label = _('Farm')
        self.fields['amount'].label = _('Amount')
        self.fields['date'].label = _('Date')
        self.fields['note'].label = _('Note')


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['farm', 'crop_name', 'quantity', 'unit', 'price_per_unit', 'date', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['farm'].queryset = Farm.objects.filter(owner=user)
        self.fields['farm'].required = False
        self.fields['farm'].label = _('Farm')
        self.fields['crop_name'].label = _('Crop name')
        self.fields['quantity'].label = _('Quantity')
        self.fields['unit'].label = _('Unit')
        self.fields['price_per_unit'].label = _('Price per unit')
        self.fields['date'].label = _('Date')
        self.fields['note'].label = _('Note')


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['plot', 'date', 'title', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'}), 'note': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plot'].queryset = self.fields['plot'].queryset.filter(farm__owner=user)
        self.fields['plot'].required = False
        self.fields['plot'].label = _('Field')
        self.fields['date'].label = _('Date')
        self.fields['title'].label = _('Title')
        self.fields['note'].label = _('Note')


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['plot', 'title', 'due_date']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plot'].queryset = self.fields['plot'].queryset.filter(farm__owner=user)
        self.fields['plot'].required = False
        self.fields['plot'].label = _('Field')
        self.fields['title'].label = _('Title')
        self.fields['due_date'].label = _('Due date')
