# Generated by Django 5.0.1 on 2024-01-30 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0019_alter_coordinates_lat_alter_coordinates_lng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinates',
            name='lat',
            field=models.DecimalField(decimal_places=14, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='coordinates',
            name='lng',
            field=models.DecimalField(decimal_places=14, default=0, max_digits=20),
        ),
    ]
