# Generated by Django 5.0 on 2024-01-26 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0011_rename_nodenumber_car_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='battery',
            field=models.IntegerField(default=100),
        ),
    ]
