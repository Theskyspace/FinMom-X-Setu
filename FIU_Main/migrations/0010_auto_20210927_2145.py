# Generated by Django 3.2.7 on 2021-09-27 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FIU_Main', '0009_alter_consent_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consent',
            name='Consent_ID',
        ),
        migrations.AddField(
            model_name='consent',
            name='ConsentHandle',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='consent',
            name='ConsentID',
            field=models.TextField(default=''),
        ),
    ]
