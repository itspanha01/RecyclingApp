from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PlasticSubmission

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = PlasticSubmission
        fields = ['plastic_type', 'quantity', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 50}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional: where did you collect these?'}),
        }