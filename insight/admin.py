from django.contrib import admin

from insight.models import Article, CoronaCase, CountryTracker, Prognosis, ScrapeSite, Source

class SourceInline(admin.TabularInline):
    model = Source

class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        SourceInline,
    ]

admin.site.register(Article, ArticleAdmin)
admin.site.register(Source)
admin.site.register(CoronaCase)
admin.site.register(ScrapeSite)
admin.site.register(Prognosis)
admin.site.register(CountryTracker)
