from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, Form

from secretcrushapp.models import HidentoUser, ContactHidento

class SignUpForm(ModelForm):
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput,)

    class Meta:
        model = get_user_model()
        fields = ('firstname', 'lastname', 'email', 'gender')

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        try:
            password_validation.validate_password(password, self.instance)
        except forms.ValidationError as error:
            self.add_error('password', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = generateUsername(self.cleaned_data['firstname'], self.cleaned_data['lastname'])
        if commit:
            user.save()
        return user

def generateUsername(firstname, lastname):
    username = firstname.lower() + '_' + lastname.lower()
    number = 0
    newUsername = username
    try:
        while True:
            HidentoUser.objects.get(username=newUsername)
            number = number + 1
            newUsername = username + str(number)
    except:
        return newUsername

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
    crushMessage = forms.CharField(label='Your Message', max_length=3000, required=False, widget=forms.Textarea)
    whomToInform = forms.ChoiceField(
        label='Who should be informed, if matched?',
        choices=[(1, 'Choose at random'), (2, 'Inform my crush')],
        initial=1,
        widget=forms.RadioSelect
    )

    def clean_crushUsername(self):
        crush_instagram_username = self.cleaned_data['crushUsername']
        if ' ' in crush_instagram_username:
            raise forms.ValidationError('Instagram usernames cannot contain space')
        return crush_instagram_username

class EditCrushForm(Form):
    def __init__(self, lowest_priority, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priorityPosition'] = forms.ChoiceField(
            choices=[(self.getPosition(position)) for position in range(1, lowest_priority+1)],
            label='Priority Position'
        )

    def getPosition(self, position):
        return (position, str(position)+' - Highest' if position == 1 else str(position))

    crushNickname = forms.CharField(label='Nickname for your crush', max_length=255, required=False)
    crushMessage = forms.CharField(label='Your Message', max_length=3000, required=False, widget=forms.Textarea)
    whomToInform = forms.ChoiceField(
        label='Who should be informed, if matched?',
        choices=[(1, 'Choose at random'), (2, 'Inform my crush')],
        widget=forms.RadioSelect
    )
    active = forms.BooleanField(label='Active Status')

class ContactForm(ModelForm):
    class Meta:
        model = ContactHidento
        fields = ('fullname', 'email', 'message')