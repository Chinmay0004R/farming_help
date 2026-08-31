from django import forms
from .models import Device
from plots.models import Plot
from django.utils.translation import gettext_lazy as _


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'name', 'plot']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        
        self.fields['device_id'].label = _('Device ID')
        self.fields['name'].label = _('Sensor name')
        self.fields['plot'].label = _('Field')
        self.fields['device_id'].widget.attrs['placeholder'] = _('For example, esp32-soil-sensor-01')
        self.fields['name'].widget.attrs['placeholder'] = _('For example, north field sensor')
        
        if user:
            self.fields['plot'].queryset = Plot.objects.filter(farm__owner=user)
