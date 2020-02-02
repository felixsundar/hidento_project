from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, Form

from secretcrushapp.models import HidentoUser, ContactHidento, AnonymousMessage

class SignUpForm(ModelForm):
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput,)

    class Meta:
        model = get_user_model()
        fields = ('fullname', 'email', 'gender')

    def clean_fullname(self):
        user_fullname = self.cleaned_data['fullname']
        if not alphaspace(user_fullname):
            raise forms.ValidationError('Name can contain only alphabets and spaces.')
        return user_fullname

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
        user.username = generateUsername(self.cleaned_data['fullname'])
        if commit:
            user.save()
        return user

def alphaspace(fullname):
    return all(letter.isalpha() or letter.isspace() for letter in fullname)

def generateUsername(fullname):
    username = fullname.lower().replace(' ', '_')
    username = username[:min(25, len(username))]
    number = 0
    newUsername = username
    try:
        while True:
            HidentoUser.objects.get(username=newUsername)
            number = number + 1
            newUsername = username + str(number)
    except:
        return newUsername

def getFirstname(fullname):
    return fullname.split(' ')[0].capitalize()

class HidentoUserChangeFormForUsers(ModelForm):
    class Meta:
        model = HidentoUser
        fields = ('fullname', 'username', 'email', 'date_of_birth', 'gender')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_fullname(self):
        user_fullname = self.cleaned_data['fullname']
        if not alphaspace(user_fullname):
            raise forms.ValidationError('Name can contain only alphabets and spaces.')
        return user_fullname

class AddCrushForm(Form):
    def __init__(self, lowest_priority, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priorityPosition'] = forms.ChoiceField(
            choices=[(self.getPosition(position)) for position in range(1, lowest_priority+1)],
            label='Priority Position',
            initial=str(lowest_priority)
        )

    def getPosition(self, position):
        return (str(position), str(position)+' - Highest' if position == 1 else str(position))

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
            raise forms.ValidationError('Instagram usernames cannot contain spaces.')

        return crush_instagram_username

class EditCrushForm(Form):
    def __init__(self, lowest_priority, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priorityPosition'] = forms.ChoiceField(
            choices=[(self.getPosition(position)) for position in range(1, lowest_priority+1)],
            label='Priority Position'
        )

    def getPosition(self, position):
        return (str(position), str(position)+' - Highest' if position == 1 else str(position))

    crushNickname = forms.CharField(label='Nickname for your crush', max_length=255, required=False)
    crushMessage = forms.CharField(label='Your Message', max_length=3000, required=False, widget=forms.Textarea)
    whomToInform = forms.ChoiceField(
        label='Who should be informed, if matched?',
        choices=[(1, 'Choose at random'), (2, 'Inform my crush')],
        widget=forms.RadioSelect
    )
    active = forms.BooleanField(label='Active Status', required=False)

class ContactForm(ModelForm):
    class Meta:
        model = ContactHidento
        fields = ('fullname', 'email', 'message')

class SendMessageForm(ModelForm):
    class Meta:
        model = AnonymousMessage
        fields = ('receiver_instagram_username', 'message', 'sender_nickname')

    def clean_receiver_instagram_username(self):
        receiver_instagram_username = self.cleaned_data['receiver_instagram_username']
        if ' ' in receiver_instagram_username:
            raise forms.ValidationError('Instagram usernames cannot contain spaces.')
        return receiver_instagram_username

class MessageBlacklistForm(Form):
    nickname1 = forms.CharField(label='Nickname', max_length=40, required=False)
    username1 = forms.CharField(label='Username', max_length=40, required=True)
    nickname2 = forms.CharField(label='Nickname', max_length=40, required=False)
    username2 = forms.CharField(label='Username', max_length=40, required=True)
    nickname3 = forms.CharField(label='Nickname', max_length=40, required=False)
    username3 = forms.CharField(label='Username', max_length=40, required=True)
    nickname4 = forms.CharField(label='Nickname', max_length=40, required=False)
    username4 = forms.CharField(label='Username', max_length=40, required=True)
    nickname5 = forms.CharField(label='Nickname', max_length=40, required=False)
    username5 = forms.CharField(label='Username', max_length=40, required=True)
    nickname6 = forms.CharField(label='Nickname', max_length=40, required=False)
    username6 = forms.CharField(label='Username', max_length=40, required=True)
    nickname7 = forms.CharField(label='Nickname', max_length=40, required=False)
    username7 = forms.CharField(label='Username', max_length=40, required=True)
    nickname8 = forms.CharField(label='Nickname', max_length=40, required=False)
    username8 = forms.CharField(label='Username', max_length=40, required=True)
    nickname9 = forms.CharField(label='Nickname', max_length=40, required=False)
    username9 = forms.CharField(label='Username', max_length=40, required=True)
    nickname10 = forms.CharField(label='Nickname', max_length=40, required=False)
    username10 = forms.CharField(label='Username', max_length=40, required=True)