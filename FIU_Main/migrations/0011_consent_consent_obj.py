# Generated by Django 3.2.7 on 2021-10-02 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FIU_Main', '0010_auto_20210927_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='consent',
            name='consent_obj',
            field=models.TextField(default=''),
        ),
    ]
