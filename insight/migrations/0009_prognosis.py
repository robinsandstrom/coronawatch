# Generated by Django 3.0.4 on 2020-03-12 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0008_scrapesite_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prognosis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('offset', models.IntegerField(default=0)),
            ],
        ),
    ]
