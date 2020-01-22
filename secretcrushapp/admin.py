from django import forms
from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group

from secretcrushapp.models import InstagramCrush, HidentoUser, Controls, ContactHidento, HowItWorks, FAQ, InstagramDetails

class HidentoUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
        fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = HidentoUser
        fields = ('username', 'email', 'firstname', 'fullname', 'gender')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class HidentoUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
        the user, but replaces the password field with admin's
        password hash display field.
        """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = HidentoUser
        fields = ('userid', 'firstname', 'fullname', 'username', 'email', 'date_of_birth', 'gender', 'password', 'joined_time',
                  'is_staff', 'is_superuser', 'is_active')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class HidentoUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = HidentoUserChangeForm
    add_form = HidentoUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    #list_display fields are displayed in the table of user details
    list_display = ('userid', 'username', 'email', 'firstname', 'fullname', 'gender', 'date_of_birth', 'joined_time',
                    'is_staff', 'is_superuser', 'is_active')
    #list_filter fields are shown on the side of admin site for filtering based on its values
    list_filter = ('is_superuser', 'is_staff')
    #fieldsets define how the user details are displayed in the edit user details page
    fieldsets = (
        ('Credentials', {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('firstname', 'fullname', 'date_of_birth', 'gender', 'joined_time')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    #add_fieldsets are fields that will be required while creating a new user from admin page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'firstname', 'fullname', 'gender', 'password1', 'password2')}
        ),
    )
    search_fields = ('username', 'email', 'firstname', 'fullname')
    ordering = ('username', 'email', 'firstname', 'fullname')
    filter_horizontal = ()

class ContactHidentoAdmin(admin.ModelAdmin):
    search_fields = ('email', 'fullname', 'message')
    list_filter = ('is_replied', 'is_successfully_replied', 'is_important')

# Now register the new UserAdmin...
admin.site.register(HidentoUser, HidentoUserAdmin)
admin.site.register(InstagramCrush)
admin.site.register(Controls)
admin.site.register(ContactHidento, ContactHidentoAdmin)
admin.site.register(HowItWorks)
admin.site.register(FAQ)
admin.site.register(InstagramDetails)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)