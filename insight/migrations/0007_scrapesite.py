# Generated by Django 3.0.4 on 2020-03-12 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0006_coronacase_backup'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapeSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
            ],
        ),
    ]