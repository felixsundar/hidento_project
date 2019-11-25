# Generated by Django 2.2.7 on 2019-11-23 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('gender', models.IntegerField(blank=True, choices=[(1, 'Male'), (2, 'Female'), (3, 'Others')], null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstagramCrush',
            fields=[
                ('hidento_userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='instagramDetails', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('instagram_userid', models.CharField(max_length=255, unique=True)),
                ('instagram_username', models.CharField(max_length=255, unique=True)),
                ('crush1_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush1_time', models.DateTimeField(blank=True, null=True)),
                ('crush1_active', models.BooleanField(default=False)),
                ('crush2_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush2_time', models.DateTimeField(blank=True, null=True)),
                ('crush2_active', models.BooleanField(default=False)),
                ('crush3_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush3_time', models.DateTimeField(blank=True, null=True)),
                ('crush3_active', models.BooleanField(default=False)),
                ('crush4_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush4_time', models.DateTimeField(blank=True, null=True)),
                ('crush4_active', models.BooleanField(default=False)),
                ('crush5_username', models.CharField(blank=True, max_length=255, null=True)),
                ('crush5_time', models.DateTimeField(blank=True, null=True)),
                ('crush5_active', models.BooleanField(default=False)),
                ('currently_matched', models.BooleanField(default=False)),
                ('match_instagram_username', models.CharField(blank=True, max_length=255, null=True)),
                ('match_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
