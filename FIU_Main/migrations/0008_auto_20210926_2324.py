# Generated by Django 3.2.7 on 2021-09-26 17:54

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('FIU_Main', '0007_auto_20210926_2258'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='Consent',
        ),
        migrations.RenameField(
            model_name='consent',
            old_name='bio',
            new_name='Consent_ID',
        ),
    ]
