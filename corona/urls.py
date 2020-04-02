from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

from insight.views import modeling

urlpatterns = [
    path('', include('insight.urls')),
    path('admin/', admin.site.urls),
]
urlpatterns += i18n_patterns(
    path('modeling', modeling, name='modeling'),
)
