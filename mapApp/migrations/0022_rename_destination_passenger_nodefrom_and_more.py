# Generated by Django 5.0.1 on 2024-02-05 05:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0021_rename_node_car_nodefrom_car_nodeto'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passenger',
            old_name='destination',
            new_name='nodeFrom',
        ),
        migrations.RenameField(
            model_name='passenger',
            old_name='origin',
            new_name='nodeTo',
        ),
        migrations.RemoveField(
            model_name='coordinates',
            name='car',
        ),
        migrations.RemoveField(
            model_name='coordinates',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='coordinates',
            name='lng',
        ),
        migrations.AddField(
            model_name='coordinates',
            name='callTime',
            field=models.TimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='coordinates',
            name='nodeFrom',
            field=models.CharField(default='1', max_length=20),
        ),
        migrations.AddField(
            model_name='coordinates',
            name='nodeTo',
            field=models.CharField(default='0', max_length=20),
        ),
        migrations.AddField(
            model_name='passenger',
            name='callTime',
            field=models.TimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='passenger',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]
