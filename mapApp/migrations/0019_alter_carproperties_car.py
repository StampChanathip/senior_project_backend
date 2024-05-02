# Generated by Django 5.0.1 on 2024-03-27 06:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0018_carproperties_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carproperties',
            name='car',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='mapApp.car'),
        ),
    ]
