from django.contrib import admin

# Register your models here.
from insight.models import CoronaCase, CountryTracker, ScrapeSite, Prognosis

admin.site.register(CoronaCase)
admin.site.register(ScrapeSite)
admin.site.register(Prognosis)
admin.site.register(CountryTracker)
