# Generated by Django 5.0.1 on 2024-05-02 04:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0027_alter_carproperties_lastchargetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboarddata',
            name='carId',
            field=models.CharField(default='1', max_length=20),
        ),
        migrations.AddField(
            model_name='dashboarddata',
            name='totalEmptyTripLength',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dashboarddata',
            name='totalServiceLength',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ChargeLap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chargeLap', models.CharField(default='1', max_length=20)),
                ('tripLengthToCharge', models.IntegerField(default=0)),
                ('car', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='chargeLap', to='mapApp.dashboarddata')),
            ],
        ),
    ]
