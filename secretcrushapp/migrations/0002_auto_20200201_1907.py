# Generated by Django 2.2.7 on 2020-02-01 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretcrushapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hidentouser',
            name='firstname',
            field=models.CharField(max_length=20),
        ),
    ]