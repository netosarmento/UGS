# Generated by Django 5.2 on 2025-05-16 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0024_medicine_medicinelog_medicineusage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicine',
            name='lab',
            field=models.CharField(max_length=100),
        ),
    ]
