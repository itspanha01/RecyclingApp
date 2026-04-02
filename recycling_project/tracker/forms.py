from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import RecyclingEntry

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RecyclingEntryForm(forms.ModelForm):
    class Meta:
        model = RecyclingEntry
        fields = ['material', 'weight_kg', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }