from django.db import models

# Create your models here.

class CoronaCase(models.Model):

    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    infected = models.IntegerField(default=0)
