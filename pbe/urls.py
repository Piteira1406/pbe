from django.contrib import admin
from django.urls import path, include
from django.apps import apps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include(apps.get_app_config('oscar').urls[0])),
    path('api/', include([
        path('', include('oscarapi.urls')),
        path('', include('marketplace.urls')),
    ])),


    path("api/oscar/", include("oscarapi.urls")),
    
    path("api/", include("marketplace.urls"))  # A tua API
]