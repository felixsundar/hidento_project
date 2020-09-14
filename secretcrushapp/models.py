import logging
import threading

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models, transaction

# Create your models here.
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from secretcrushapp import matching

from hidento_project import settings

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)
class HidentoUserManager(BaseUserManager):
    def create_user(self, username, email, firstname, fullname, gender, password):
        if not (username and email and firstname and fullname and gender):
            raise ValueError('Users must have a username, an email address, a firstname and a fullname')

        user = self.model(
            username = username,
            email=self.normalize_email(email),
            firstname = firstname,
            fullname = fullname,
            gender = gender
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, firstname, fullname, gender, password):
        user = self.create_user(username, email, firstname, fullname, gender, password)
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
    username = models.CharField(max_length=35, unique=True, blank=False, null=False)
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True, blank=False, null=False)
    firstname = models.CharField(max_length=20)
    fullname = models.CharField(verbose_name='Full Name', max_length=40)
    gender = models.IntegerField(choices=[(1,'Male'), (2,'Female'), (3,'Other')])
    date_of_birth = models.DateField(verbose_name='Date of Birth', blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(verbose_name='active', default=True)
    joined_time = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'firstname', 'fullname', 'gender']

    objects = HidentoUserManager()

    def __str__(self):
        return self.username

@receiver(pre_save, sender=HidentoUser, dispatch_uid='hidentoUserPreSave')
def hidentoUserPreSave(sender, **kwargs):
    hidentoUser = kwargs['instance']
    if hidentoUser.is_superuser or hidentoUser.is_staff:
        if hidentoUser.username != 'hidentosonlysuperuser':
            raise ValueError('Users cannot be upgraded to admins.')
    firstname = hidentoUser.fullname.split(' ')[0].capitalize()
    hidentoUser.firstname = firstname[:min(20, len(firstname))]

@receiver(post_save, sender=HidentoUser, dispatch_uid='hidentoUserPostSave')
def hidentoUserPostSave(sender, **kwargs):
    hidentoUser = kwargs['instance']
    if hidentoUser.is_superuser or hidentoUser.is_staff:
        if hidentoUser.username != 'hidentosonlysuperuser':
            hidentoUser.is_staff = False
            hidentoUser.is_superuser = False
            hidentoUser.save()

class Controls(models.Model):
    control_id = models.CharField(max_length=40, unique=True, primary_key=True)
    stablization_days = models.IntegerField(default=7)
    stable_days = models.IntegerField(default=14)
    stablizer_thread = models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Start Stablizer thread')], default=1)
    stablizer_thread_status = models.IntegerField(choices=[(1, 'Stablizer thread running'), (2, 'Stablizer thread not running'),
                                                           (3, 'Check stablizer thread')], default=2)
    number_of_threads = models.IntegerField(default=0)
    total_matches = models.BigIntegerField(default=0)
    total_stable_matches = models.BigIntegerField(default=0)
    total_unstable_matches = models.BigIntegerField(default=0)
    total_users = models.BigIntegerField(default=0)
    total_users_with_instagram_linked = models.BigIntegerField(default=0)
    total_male_users = models.BigIntegerField(default=0)
    total_female_users = models.BigIntegerField(default=0)
    total_other_gender_users = models.BigIntegerField(default=0)
    count_updated_time = models.DateTimeField(blank=True, null=True)
    count_users_and_matches = models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Count Now')], default=1)


    def save(self, *args, **kwargs):
        if self.stablizer_thread == 2:
            if not stablizer_thread_running():
                from secretcrushapp import stablizer
                stablizer.startStablizerThread()
        self.stablizer_thread = 1
        if self.stablizer_thread_status == 3:
            if stablizer_thread_running():
                self.stablizer_thread_status = 1
            else:
                self.stablizer_thread_status = 2
        if self.count_users_and_matches == 2:
            total_matched_instagrams = InstagramCrush.objects.filter(match_instagram_username__isnull=False).count()
            total_stable_matched_instagrams = InstagramCrush.objects.filter(match_instagram_username__isnull=False,
                                                                            match_stablized=True).count()
            total_unstable_matched_instagrams = InstagramCrush.objects.filter(match_instagram_username__isnull=False,
                                                                            match_stablized=False).count()
            self.total_matches = total_matched_instagrams//2
            self.total_stable_matches = total_stable_matched_instagrams//2
            self.total_unstable_matches = total_unstable_matched_instagrams//2
            self.total_users = HidentoUser.objects.all().count()
            self.total_users_with_instagram_linked = InstagramCrush.objects.all().count()
            self.total_male_users = HidentoUser.objects.filter(gender=1).count()
            self.total_female_users = HidentoUser.objects.filter(gender=2).count()
            self.total_other_gender_users = HidentoUser.objects.filter(gender=3).count()
            self.count_updated_time = now()
            self.number_of_threads = len(threading.enumerate())
        self.count_users_and_matches = 1
        super().save(*args, **kwargs)

def stablizer_thread_running():
    thread_list = threading.enumerate()
    for thread in thread_list:
        if thread.name == 'stablizer_thread':
            return True
    return False

class InstagramCrush(models.Model):
    hidento_userid = models.ForeignKey(HidentoUser, related_name='instagramDetails', on_delete=models.CASCADE, primary_key=True)
    instagram_username = models.CharField(max_length=40, unique=True)
    crush1_username = models.CharField(max_length=40, blank=True, null=True)
    crush1_nickname = models.CharField(max_length=40, blank=True, null=True)
    crush1_message = models.TextField(max_length=1000, blank=True, null=True)
    crush1_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush1_time = models.DateTimeField(blank=True, null=True)
    crush1_active = models.BooleanField(default=False)
    crush2_username = models.CharField(max_length=40, blank=True, null=True)
    crush2_nickname = models.CharField(max_length=40, blank=True, null=True)
    crush2_message = models.TextField(max_length=1000, blank=True, null=True)
    crush2_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush2_time = models.DateTimeField(blank=True, null=True)
    crush2_active = models.BooleanField(default=False)
    crush3_username = models.CharField(max_length=40, blank=True, null=True)
    crush3_nickname = models.CharField(max_length=40, blank=True, null=True)
    crush3_message = models.TextField(max_length=1000, blank=True, null=True)
    crush3_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush3_time = models.DateTimeField(blank=True, null=True)
    crush3_active = models.BooleanField(default=False)
    crush4_username = models.CharField(max_length=40, blank=True, null=True)
    crush4_nickname = models.CharField(max_length=40, blank=True, null=True)
    crush4_message = models.TextField(max_length=1000, blank=True, null=True)
    crush4_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush4_time = models.DateTimeField(blank=True, null=True)
    crush4_active = models.BooleanField(default=False)
    crush5_username = models.CharField(max_length=40, blank=True, null=True)
    crush5_nickname = models.CharField(max_length=40, blank=True, null=True)
    crush5_message = models.TextField(max_length=1000, blank=True, null=True)
    crush5_whomToInform = models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)
    crush5_time = models.DateTimeField(blank=True, null=True)
    crush5_active = models.BooleanField(default=False)
    match_instagram_username = models.CharField(max_length=40, blank=True, null=True)
    match_time = models.DateTimeField(blank=True, null=True)
    old_match_instagram_username = models.CharField(max_length=40, blank=True, null=True)
    old_match_time = models.DateTimeField(blank=True, null=True)
    old_match_broken_time = models.DateTimeField(blank=True, null=True)
    match_stablized = models.BooleanField(default=False)
    inform_this_user = models.BooleanField(default=False)
    match_stablized_time = models.DateTimeField(blank=True, null=True)
    match_nickname = models.CharField(max_length=40, blank=True, null=True)
    match_message = models.TextField(max_length=1000, blank=True, null=True)

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
        if self._state.adding and self.instagramDetailsNotPresent():
            raise ValueError('Instagram username must match the instagram details of the user.')
        crushListModified = self._state.adding or self.isPreferenceListModified()
        super().save(*args, **kwargs)
        if crushListModified:
            matching_thread = threading.Thread(target=matching.startMatching, daemon=True, args=(self.hidento_userid,))
            matching_thread.start()

    def instagramDetailsModified(self):
        if not self._state.adding:
            if self.instagram_username != self._loaded_values['instagram_username']:
                return True
        return False

    def instagramDetailsNotPresent(self):
        user_instagramDetails = self.hidento_userid.user_instagramDetails.first()
        if user_instagramDetails is None or user_instagramDetails.instagram_username != self.instagram_username:
            return True
        return False

    def isPreferenceListModified(self):
        if not self._state.adding:
            for position in range(1,6):
                if self.__dict__[getCrushField(position, 'username')] != self._loaded_values[getCrushField(position, 'username')] \
                    or self.__dict__[getCrushField(position, 'active')] != self._loaded_values[getCrushField(position, 'active')]:
                    return True
        return False

def getCrushField(position, fieldname):
        return 'crush' + str(position) + '_' + fieldname

@transaction.atomic
@receiver(post_delete, sender=InstagramCrush, dispatch_uid='instagramPostDelete')
def userInstagramPostDelete(sender, **kwargs):
    user_instagram = kwargs['instance']
    loser = matching.breakCurrentMatch(user_instagram)
    if loser is not None:
        loser.save()
        matching_thread = threading.Thread(target=matching.startMatching, daemon=True,
                                               args=(loser.hidento_userid,))
        matching_thread.start()
    user_instagramDetails = user_instagram.hidento_userid.user_instagramDetails.select_for_update().first()
    if user_instagramDetails is not None:
        user_instagramDetails.delete()

class InstagramDetails(models.Model):
    hidento_userid = models.ForeignKey(HidentoUser, related_name='user_instagramDetails', on_delete=models.CASCADE, primary_key=True)
    instagram_userid = models.CharField(max_length=40, unique=True)
    instagram_username = models.CharField(max_length=40, unique=True)
    ll_access_token = models.CharField(max_length=1000, null=True, blank=True)
    token_expires_in = models.BigIntegerField(null=True, blank=True)
    token_time = models.DateTimeField(null=True, blank=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        if self.user_instagramDetailsModified():
            raise ValueError('Instagram account details cannot be modified. To change instagram account, '
                             'remove and link instagram again.')
        super().save(*args, **kwargs)

    def user_instagramDetailsModified(self):
        if not self._state.adding:
            if self.instagram_username != self._loaded_values['instagram_username'] \
                or self.instagram_userid != self._loaded_values['instagram_userid']:
                return True
        return False

@transaction.atomic
@receiver(post_delete, sender=InstagramDetails, dispatch_uid='instagramDetailsPostDelete')
def userInstagramDetailsPostDelete(sender, **kwargs):
    user_instagramDetails = kwargs['instance']
    user = user_instagramDetails.hidento_userid
    user_instagram = user.instagramDetails.select_for_update().first()
    if user_instagram is not None:
        user_instagram.delete()
    user.anonymousSentMessages.all().delete()


class ContactHidento(models.Model):
    fullname = models.CharField(max_length=40, null=False)
    email = models.EmailField(max_length=255, null=False)
    message = models.TextField(max_length=2000, null=False)
    contact_time = models.DateTimeField(default=timezone.now)
    reply_email_subject = models.CharField(max_length=200, null=True, blank=True)
    reply_email_message = models.TextField(max_length=3000, null=True, blank=True)
    replied_time = models.DateTimeField(blank=True, null=True)
    is_successfully_replied = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    action = models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Send Reply'), (3, 'Delete')], default=1)

    def save(self, *args, **kwargs):
        if (not self._state.adding) and self.action == 3:
            self.delete()
            return
        if self.action == 2:
            if self.reply_email_message is not None and self.reply_email_subject is not None:
                sent_status = send_mail(subject=self.reply_email_subject, message=self.reply_email_message,
                          from_email=settings.SUPPORT_FROM_EMAIL, recipient_list=[self.email], fail_silently=True)
                self.is_successfully_replied = True if sent_status == 1 else False
                self.is_replied = True
                self.replied_time = now()
        self.action = 1
        super().save(*args, **kwargs)

class HowItWorks(models.Model):
    heading = models.TextField(max_length=100, null=False)
    explanation = models.TextField(max_length=2000, null=False)
    is_enabled = models.BooleanField(default=True)
    priority_value = models.IntegerField(null=False, default=1)

class FAQ(models.Model):
    question = models.TextField(max_length=300, null=False)
    answer = models.TextField(max_length=2000, null=False)
    is_enabled = models.BooleanField(default=True)
    priority_value = models.IntegerField(null=False, default=1)

class AnonymousMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True, unique=True)
    hidento_userid = models.ForeignKey(HidentoUser, related_name='anonymousSentMessages', on_delete=models.DO_NOTHING)
    sender_instagram_username = models.CharField(max_length=40, null=False)
    receiver_instagram_username1 = models.CharField(max_length=40, null=False)
    receiver_instagram_username2 = models.CharField(max_length=40, null=False)
    message = models.TextField(max_length=1000, null=False)
    added_time = models.DateTimeField(null=False)
    is_hidden = models.BooleanField(default=False)
    is_abusive = models.BooleanField(default=False)

class MessageBlacklist(models.Model):
    hidento_userid = models.ForeignKey(HidentoUser, related_name='messageBlacklist', on_delete=models.CASCADE, primary_key=True)
    blacklistJSON = JSONField(null=True, blank=True)
    last_modified_time = models.DateTimeField(null=False)