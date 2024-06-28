from django.contrib import admin
from django.urls import path, include

# URL patterns for the tcg_project project
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('card_manager.urls')),
]
