# Generated by Django 5.0.1 on 2024-03-27 06:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0016_alter_carproperties_arrivaltime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carproperties',
            name='arrivalTime',
            field=models.TimeField(blank=True, default=datetime.datetime.now),
        ),
    ]