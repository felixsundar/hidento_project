from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from secretcrushapp.models import HidentoUser


class SignUpForm(UserCreationForm):
    firstname = forms.CharField(label="First Name", required=True)
    lastname = forms.CharField(label="Last Name", required=True)
    username = forms.CharField(label="Username", required=True)
    email = forms.EmailField(label="Email", required=True)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = get_user_model()
        fields = ('firstname', 'lastname', 'username', 'email')

class HidentoUserChangeFormForUsers(ModelForm):
    class Meta:
        model = HidentoUser
        fields = ('firstname', 'lastname', 'username', 'email', 'date_of_birth', 'gender')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }