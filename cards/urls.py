from django.urls import path
from .views import CardNameView, UpdateCardsView


urlpatterns = [
    path('card/', CardNameView.as_view(), name='card-name'),
    path('update-cards/', UpdateCardsView.as_view(), name='update-cards'),
]
