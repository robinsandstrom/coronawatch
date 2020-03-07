from django.db import models

# Create your models here.

region_codes = {
    '01':'Stockholm',
    '03':'Uppsala',
    '04':'Södermanland',
    '05':'Östergötland',
    '06':'Jönköping',
    '07':'Kronoberg',
    '08':'Kalmar',
    '09':'Gotland',
    '10':'Blekinge',
    '12':'Skåne',
    '13':'Halland',
    '14':'Västra Götaland',
    '17':'Värmland',
    '18':'Örebro',
    '19':'Västmanland',
    '20':'Dalarna',
    '21':'Gävleborg',
    '22':'Västernorrland',
    '23':'Jämtland',
    '24':'Västerbotten',
    '25':'Norrbotten',
}

class CoronaCase(models.Model):

    date = models.DateTimeField(blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    infected = models.IntegerField(default=0)

    def __str__(self):

        return str(self.date) + ' ' + str(self.region) + ' ' + str(self.text) + ' ' + str(self.infected)
