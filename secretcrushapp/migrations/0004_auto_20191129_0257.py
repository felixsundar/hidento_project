# Generated by Django 2.2.7 on 2019-11-28 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretcrushapp', '0003_auto_20191127_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramcrush',
            name='inform_this_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='instagramcrush',
            name='match_stablized',
            field=models.BooleanField(default=False),
        ),
    ]