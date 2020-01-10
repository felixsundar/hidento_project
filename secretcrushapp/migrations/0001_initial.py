# Generated by Django 2.2.7 on 2020-01-10 07:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='HidentoUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('userid', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email')),
                ('firstname', models.CharField(max_length=255)),
                ('fullname', models.CharField(max_length=255, verbose_name='Full Name')),
                ('gender', models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other')])),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('joined_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContactHidento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('message', models.TextField(max_length=3000)),
                ('contact_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('reply_email_subject', models.CharField(blank=True, max_length=300, null=True)),
                ('reply_email_message', models.TextField(blank=True, max_length=6000, null=True)),
                ('replied_time', models.DateTimeField(blank=True, null=True)),
                ('is_successfully_replied', models.BooleanField(default=False)),
                ('is_replied', models.BooleanField(default=False)),
                ('is_important', models.BooleanField(default=False)),
                ('action', models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Send Reply'), (3, 'Delete')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Controls',
            fields=[
                ('control_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('stablization_days', models.IntegerField(default=7)),
                ('stable_days', models.IntegerField(default=14)),
                ('stablizer_thread', models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Start Stablizer thread')], default=1)),
                ('stablizer_thread_status', models.IntegerField(choices=[(1, 'Stablizer thread running'), (2, 'Stablizer thread not running'), (3, 'Check stablizer thread')], default=2)),
                ('number_of_threads', models.IntegerField(default=0)),
                ('total_matches', models.BigIntegerField(default=0)),
                ('total_stable_matches', models.BigIntegerField(default=0)),
                ('total_unstable_matches', models.BigIntegerField(default=0)),
                ('total_users', models.BigIntegerField(default=0)),
                ('total_users_with_instagram_linked', models.BigIntegerField(default=0)),
                ('total_male_users', models.BigIntegerField(default=0)),
                ('total_female_users', models.BigIntegerField(default=0)),
                ('total_other_gender_users', models.BigIntegerField(default=0)),
                ('count_updated_time', models.DateTimeField(blank=True, null=True)),
                ('count_users_and_matches', models.IntegerField(choices=[(1, 'Do Nothing'), (2, 'Count Now')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(max_length=3000)),
                ('answer', models.TextField(max_length=10000)),
                ('is_enabled', models.BooleanField(default=True)),
                ('priority_value', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='HowItWorks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.TextField(max_length=3000)),
                ('explanation', models.TextField(max_length=10000)),
                ('is_enabled', models.BooleanField(default=True)),
                ('priority_value', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='InstagramCrush',
            fields=[
                ('hidento_userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='instagramDetails', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('instagram_userid', models.CharField(max_length=255, unique=True)),
                ('instagram_username', models.CharField(max_length=255, unique=True)),
                ('crush1_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush1_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('crush1_message', models.TextField(blank=True, max_length=3000, null=True)),
                ('crush1_whomToInform', models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)),
                ('crush1_time', models.DateTimeField(blank=True, null=True)),
                ('crush1_active', models.BooleanField(default=False)),
                ('crush2_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush2_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('crush2_message', models.TextField(blank=True, max_length=3000, null=True)),
                ('crush2_whomToInform', models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)),
                ('crush2_time', models.DateTimeField(blank=True, null=True)),
                ('crush2_active', models.BooleanField(default=False)),
                ('crush3_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush3_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('crush3_message', models.TextField(blank=True, max_length=3000, null=True)),
                ('crush3_whomToInform', models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)),
                ('crush3_time', models.DateTimeField(blank=True, null=True)),
                ('crush3_active', models.BooleanField(default=False)),
                ('crush4_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush4_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('crush4_message', models.TextField(blank=True, max_length=3000, null=True)),
                ('crush4_whomToInform', models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)),
                ('crush4_time', models.DateTimeField(blank=True, null=True)),
                ('crush4_active', models.BooleanField(default=False)),
                ('crush5_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush5_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('crush5_message', models.TextField(blank=True, max_length=3000, null=True)),
                ('crush5_whomToInform', models.IntegerField(choices=[(1, 'Choose at random'), (2, 'Inform my crush')], default=1)),
                ('crush5_time', models.DateTimeField(blank=True, null=True)),
                ('crush5_active', models.BooleanField(default=False)),
                ('match_instagram_username', models.CharField(blank=True, max_length=255, null=True)),
                ('match_time', models.DateTimeField(blank=True, null=True)),
                ('old_match_instagram_username', models.CharField(blank=True, max_length=255, null=True)),
                ('old_match_time', models.DateTimeField(blank=True, null=True)),
                ('old_match_broken_time', models.DateTimeField(blank=True, null=True)),
                ('match_stablized', models.BooleanField(default=False)),
                ('inform_this_user', models.BooleanField(default=False)),
                ('match_stablized_time', models.DateTimeField(blank=True, null=True)),
                ('match_nickname', models.CharField(blank=True, max_length=255, null=True)),
                ('match_message', models.TextField(blank=True, max_length=3000, null=True)),
            ],
        ),
    ]
