# Generated by Django 5.0.1 on 2024-01-30 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0016_rename_positions_coordinates_carid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coordinates',
            old_name='carId',
            new_name='car',
        ),
    ]
