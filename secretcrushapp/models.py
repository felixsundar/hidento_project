import logging
import threading
import time

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models

# Create your models here.
from django.utils.timezone import now
from secretcrushapp import matching
from secretcrushapp import testcase

from hidento_project import settings

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)
class HidentoUserManager(BaseUserManager):
    def create_user(self, username, email, firstname, lastname, password):
        if not (username and email and firstname and lastname):
            raise ValueError('Users must have a username, an email address, a firstname and a lastname')

        user = self.model(
            username = username,
            email=self.normalize_email(email),
            firstname = firstname,
            lastname = lastname
        )

        user.set_password(password)
        user.joined_time = now()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, firstname, lastname, password):
        user = self.create_user(username, email, firstname, lastname, password)
        #is_staff is the field name which django will check to provide access to admin site. even for superusers.
        #it provides only access to admin site. if the user didn't have other permissions, admin site will be
        #accessible but it will be empty
        user.is_staff = True
        #is_superuser is a field from PermissionsMixin. if it is true all permissions are granted by default
        user.is_superuser = True
        user.save(using=self._db)
        return user


class HidentoUser(AbstractBaseUser, PermissionsMixin):
    userid = models.BigAutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    gender = models.IntegerField(choices=[(1,'Male'), (2,'Female'), (3,'Others')], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(verbose_name='active', default=True)
    joined_time = models.DateTimeField(blank=False, null=False)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'firstname', 'lastname']

    objects = HidentoUserManager()

    def __str__(self):
        return self.username


class InstagramCrush(models.Model):
    hidento_userid = models.ForeignKey(HidentoUser, related_name='instagramDetails', on_delete=models.CASCADE, primary_key=True)
    instagram_userid = models.CharField(max_length=255, unique=True)
    instagram_username = models.CharField(max_length=255, unique=True)
    crush1_username = models.CharField(max_length=255, blank=True, null=True)
    crush1_nickname = models.CharField(max_length=255, blank=True, null=True)
    crush1_message = models.TextField(max_length=3000, blank=True, null=True)
    crush1_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush1_time = models.DateTimeField(blank=True, null=True)
    crush1_active = models.BooleanField(default=False)
    crush2_username = models.CharField(max_length=255, blank=True, null=True)
    crush2_nickname = models.CharField(max_length=255, blank=True, null=True)
    crush2_message = models.TextField(max_length=3000, blank=True, null=True)
    crush2_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush2_time = models.DateTimeField(blank=True, null=True)
    crush2_active = models.BooleanField(default=False)
    crush3_username = models.CharField(max_length=255, blank=True, null=True)
    crush3_nickname = models.CharField(max_length=255, blank=True, null=True)
    crush3_message = models.TextField(max_length=3000, blank=True, null=True)
    crush3_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush3_time = models.DateTimeField(blank=True, null=True)
    crush3_active = models.BooleanField(default=False)
    crush4_username = models.CharField(max_length=255, blank=True, null=True)
    crush4_nickname = models.CharField(max_length=255, blank=True, null=True)
    crush4_message = models.TextField(max_length=3000, blank=True, null=True)
    crush4_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush4_time = models.DateTimeField(blank=True, null=True)
    crush4_active = models.BooleanField(default=False)
    crush5_username = models.CharField(max_length=255, blank=True, null=True)
    crush5_nickname = models.CharField(max_length=255, blank=True, null=True)
    crush5_message = models.TextField(max_length=3000, blank=True, null=True)
    crush5_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush5_time = models.DateTimeField(blank=True, null=True)
    crush5_active = models.BooleanField(default=False)
    match_instagram_username = models.CharField(max_length=255, blank=True, null=True)
    match_time = models.DateTimeField(blank=True, null=True)
    old_match_instagram_username = models.CharField(max_length=255, blank=True, null=True)
    old_match_time = models.DateTimeField(blank=True, null=True)
    old_match_broken_time = models.DateTimeField(blank=True, null=True)
    match_stablized = models.BooleanField(default=False)
    inform_this_user = models.BooleanField(default=False)
    match_nickname = models.CharField(max_length=255, blank=True, null=True)
    match_message = models.TextField(max_length=3000, blank=True, null=True)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in InstagramCrush._meta.fields]

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        if self.instagramDetailsModified():
            raise ValueError('Instagram account details cannot be modified. To change instagram account, '
                             'remove and link instagram again.')
        crushListModified = self._state.adding or self.isPreferenceListModified()
        runtestcase = False
        if self._state.adding and self.instagram_username == 'a':
            self.crush1_username = 'e'
            self.crush1_active = True
            self.crush2_username = 'b'
            self.crush2_active = True
            runtestcase = True
        super().save(*args, **kwargs)
        if crushListModified:
            matching_thread = threading.Thread(target=matching.startMatching, daemon=True, args=(self.hidento_userid, 1, {self.hidento_userid}, None))
            matching_thread.start()
        if runtestcase:
            testcase_thread = threading.Thread(target=testcase.createTestcases, daemon=True)
            testcase_thread.start()

    def instagramDetailsModified(self):
        if not self._state.adding:
            if self.instagram_username != self._loaded_values['instagram_username'] \
                or self.instagram_userid != self._loaded_values['instagram_userid']:
                return True
        return False

    def isPreferenceListModified(self):
        if not self._state.adding:
            for position in range(1,6):
                if self.__dict__[getCrushField(position, 'username')] != self._loaded_values[getCrushField(position, 'username')] \
                    or self.__dict__[getCrushField(position, 'active')] != self._loaded_values[getCrushField(position, 'active')]:
                    return True
        return False

    def delete(self, using=None, keep_parents=False):
        loser = matching.breakCurrentMatch(self)

def getCrushField(position, fieldname):
        return 'crush' + str(position) + '_' + fieldname