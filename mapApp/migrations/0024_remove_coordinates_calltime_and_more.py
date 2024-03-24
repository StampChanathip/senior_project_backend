# Generated by Django 5.0.1 on 2024-02-05 05:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0023_alter_passenger_carid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinates',
            name='callTime',
        ),
        migrations.RemoveField(
            model_name='coordinates',
            name='nodeFrom',
        ),
        migrations.RemoveField(
            model_name='coordinates',
            name='nodeTo',
        ),
        migrations.AddField(
            model_name='coordinates',
            name='car',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='mapApp.car'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coordinates',
            name='lat',
            field=models.DecimalField(decimal_places=14, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='coordinates',
            name='lng',
            field=models.DecimalField(decimal_places=14, default=0, max_digits=20),
        ),
    ]
