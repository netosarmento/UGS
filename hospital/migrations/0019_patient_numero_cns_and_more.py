# Generated by Django 5.2 on 2025-04-29 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0018_auto_20201015_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='numero_cns',
            field=models.CharField(default=0, max_length=15),
        ),
        migrations.AddField(
            model_name='patientdischargedetails',
            name='numero_cns',
            field=models.CharField(default=0, max_length=15),
        ),
    ]
