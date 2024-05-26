from django.urls import path
from .views import CardNameView


urlpatterns = [
    path('card/', CardNameView.as_view(), name='card-name'),
]
