from django.urls import path
from django.contrib.sitemaps.views import sitemap
from insight.sitemap import StaticViewSitemap

from . import views

sitemaps = {
    'static': StaticViewSitemap
}

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('api/get_curve', views.get_curve, name='get_curve'),
    path('api/get_numbers', views.get_numbers, name='get_numbers'),
    path('modeling', views.modeling, name='modeling'),
    path('update', views.update, name='update'),
    path('excel', views.excel, name='excel'),
    path('iframe_test', views.iframe_test, name='iframe_test'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
