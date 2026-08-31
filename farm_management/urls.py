from django.contrib import admin
from django.urls import path, include
from farms.views import dashboard_view
from django.views.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('i18n/setlang/', set_language, name='set_language'),
    path('accounts/', include('accounts.urls')),
    path('farms/', include('farms.urls')),
    path('plots/', include('plots.urls')),
    path('crops/', include('crops.urls')),
    path('iot/', include('iot.urls')),
]
