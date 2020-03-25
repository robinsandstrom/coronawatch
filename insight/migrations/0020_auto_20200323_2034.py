# Generated by Django 3.0.4 on 2020-03-23 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0019_auto_20200320_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coronacase',
            name='case_type',
            field=models.CharField(choices=[('confirmed', 'Bekräftad'), ('intensive_care', 'Intensivvårdsfall'), ('death', 'Dödsfall'), ('healthy', 'Tillfrisknad')], default='confirmed', max_length=255),
        ),
        migrations.AlterField(
            model_name='coronacase',
            name='region',
            field=models.CharField(blank=True, choices=[('01', 'Stockholm'), ('03', 'Uppsala'), ('04', 'Södermanland'), ('05', 'Östergötland'), ('06', 'Jönköping'), ('07', 'Kronoberg'), ('08', 'Kalmar'), ('09', 'Gotland'), ('10', 'Blekinge'), ('12', 'Skåne'), ('13', 'Halland'), ('14', 'Västra Götaland'), ('17', 'Värmland'), ('18', 'Örebro'), ('19', 'Västmanland'), ('20', 'Dalarna'), ('21', 'Gävleborg'), ('22', 'Västernorrland'), ('23', 'Jämtland'), ('24', 'Västerbotten'), ('25', 'Norrbotten'), ('00', 'Okänd region')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='coronacase',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]