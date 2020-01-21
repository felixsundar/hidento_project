# Generated by Django 2.2.7 on 2020-01-21 17:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secretcrushapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramDetails',
            fields=[
                ('hidento_userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_instagramDetails', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('ll_access_token', models.CharField(max_length=1000)),
                ('expires_in', models.BigIntegerField()),
                ('token_time', models.DateTimeField()),
            ],
        ),
    ]
