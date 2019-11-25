from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models

# Create your models here.

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
    crush1_time = models.DateTimeField(blank=True, null=True)
    crush1_active = models.BooleanField(default=False)
    crush2_username = models.CharField(max_length=255, blank=True, null=True)
    crush2_time = models.DateTimeField(blank=True, null=True)
    crush2_active = models.BooleanField(default=False)
    crush3_username = models.CharField(max_length=255, blank=True, null=True)
    crush3_time = models.DateTimeField(blank=True, null=True)
    crush3_active = models.BooleanField(default=False)
    crush4_username = models.CharField(max_length=255, blank=True, null=True)
    crush4_time = models.DateTimeField(blank=True, null=True)
    crush4_active = models.BooleanField(default=False)
    crush5_username = models.CharField(max_length=255, blank=True, null=True)
    crush5_time = models.DateTimeField(blank=True, null=True)
    crush5_active = models.BooleanField(default=False)
    currently_matched = models.BooleanField(default=False)
    match_instagram_username = models.CharField(max_length=255, blank=True, null=True)
    match_time = models.DateTimeField(blank=True, null=True)