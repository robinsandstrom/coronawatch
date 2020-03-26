# Generated by Django 3.0.4 on 2020-03-25 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0020_auto_20200323_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coronacase',
            name='case_type',
            field=models.CharField(choices=[('confirmed', 'Bekräftad'), ('in_hospital_care', 'Nuvarande sjukvårdsfall'), ('in_intensive_care', 'Nuvarande intensivvårdsfall'), ('intensive_care', 'Intensivvårdsfall'), ('death', 'Dödsfall'), ('healthy', 'Tillfrisknad')], default='confirmed', max_length=255),
        ),
    ]
