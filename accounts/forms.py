from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('Email address'))
    first_name = forms.CharField(max_length=30, required=True, label=_('First name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last name'))
    phone_number = forms.CharField(max_length=15, required=False, label=_('Phone number'))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label=_('Address'))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = _('Choose a username')
            elif field_name == 'email':
                field.widget.attrs['placeholder'] = _('your@email.com')
            elif field_name == 'first_name':
                field.widget.attrs['placeholder'] = _('First name')
            elif field_name == 'last_name':
                field.widget.attrs['placeholder'] = _('Last name')
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = '+91 XXXXX XXXXX'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = _('Create a password')
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = _('Confirm password')


class FarmerLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': _('Username'),
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': _('Password'),
        })


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
