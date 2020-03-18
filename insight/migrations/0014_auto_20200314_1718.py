# Generated by Django 3.0.4 on 2020-03-14 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0013_countrytracker'),
    ]

    operations = [
        migrations.RenameField(
            model_name='countrytracker',
            old_name='infected',
            new_name='new_infected',
        ),
        migrations.AddField(
            model_name='countrytracker',
            name='total_infected',
            field=models.IntegerField(default=0),
        ),
    ]