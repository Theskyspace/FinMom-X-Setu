# Generated by Django 3.2.7 on 2021-10-05 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FIU_Main', '0011_consent_consent_obj'),
    ]

    operations = [
        migrations.AddField(
            model_name='consent',
            name='FirstTime',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consent',
            name='Investments',
            field=models.FloatField(default=-1),
        ),
        migrations.AddField(
            model_name='consent',
            name='Last_Updated',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='consent',
            name='Networth',
            field=models.FloatField(default=-1),
        ),
    ]
