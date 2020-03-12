from django.contrib import admin

# Register your models here.
from insight.models import CoronaCase, ScrapeSite, Prognosis

admin.site.register(CoronaCase)
admin.site.register(ScrapeSite)
admin.site.register(Prognosis)
