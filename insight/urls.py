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
    path('update', views.update, name='update'),
    path('iframe_test', views.iframe_test, name='iframe_test'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
