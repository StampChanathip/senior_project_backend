# Generated by Django 5.0.1 on 2024-04-01 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0020_rename_nodefrom_carproperties_node_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carproperties',
            old_name='node',
            new_name='nodeFrom',
        ),
        migrations.AddField(
            model_name='carproperties',
            name='nodeTo',
            field=models.CharField(default='0', max_length=20),
        ),
    ]