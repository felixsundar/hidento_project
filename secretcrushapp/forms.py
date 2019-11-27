from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, Form

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

class AddCrushForm(Form):
    def __init__(self, lowest_priority, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priorityPosition'] = forms.ChoiceField(
            choices=[(self.getPosition(position)) for position in range(1, lowest_priority+1)],
            label='Priority Position',
            initial=lowest_priority
        )

    def getPosition(self, position):
        return (position, str(position)+' - Highest' if position == 1 else str(position))

    crushUsername = forms.CharField(label='Instagram Username of your crush', max_length=255, required=True)
    crushNickname = forms.CharField(label='Nickname for your crush', max_length=255, required=False)
    crushMessage = forms.CharField(label='Your Message', max_length=3000, required=False)
    whomToInform = forms.ChoiceField(
        label='Who should be informed, if matched?',
        choices=[(1, 'Choose at random'), (2, 'Inform my crush')],
        initial=1,
        widget=forms.RadioSelect
    )

class EditCrushForm(Form):
    def __init__(self, lowest_priority, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priorityPosition'] = forms.ChoiceField(
            choices=[(self.getPosition(position)) for position in range(1, lowest_priority+1)],
            label='Priority Position'
        )

    def getPosition(self, position):
        self.has_error()
        return (position, str(position)+' - Highest' if position == 1 else str(position))

    crushUsername = forms.CharField(label='Instagram Username of your crush', max_length=255, required=True)
    crushNickname = forms.CharField(label='Nickname for your crush', max_length=255, required=False)
    crushMessage = forms.CharField(label='Your Message', max_length=3000, required=False)
    whomToInform = forms.ChoiceField(
        label='Who should be informed, if matched?',
        choices=[(1, 'Choose at random'), (2, 'Inform my crush')],
        widget=forms.RadioSelect
    )
    active = forms.BooleanField(label='Active Status')
