# Generated by Django 5.1.6 on 2025-03-24 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordatorios', '0009_alter_toma_hora'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toma',
            name='hora',
            field=models.TimeField(),
        ),
    ]
