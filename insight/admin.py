from django.contrib import admin

from insight.models import Article, CoronaCase, CountryTracker, Prognosis, ScrapeSite, Source

class SourceInline(admin.TabularInline):
    model = Source

class ScrapeSiteInline(admin.TabularInline):
    model = ScrapeSite


class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        SourceInline,
    ]

class CoronaCaseAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(CoronaCaseAdmin,self).__init__(*args, **kwargs)
        CoronaCaseAdmin.list_display = [
            'time_created',
            'case_type',
            'region',
            'date',
            'text',
            ]
        CoronaCaseAdmin.list_filter = ('case_type', 'region')

class CountryTrackerAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(CountryTrackerAdmin,self).__init__(*args, **kwargs)
        CountryTrackerAdmin.list_display = [
            'country',
            'date',
            'total_cases',
            'new_cases',
            'total_deaths',
            'new_deaths'
            ]
        CountryTrackerAdmin.list_filter = ('country', 'date')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Source)
admin.site.register(CoronaCase, CoronaCaseAdmin)
admin.site.register(ScrapeSite)
admin.site.register(Prognosis)
admin.site.register(CountryTracker, CountryTrackerAdmin)
