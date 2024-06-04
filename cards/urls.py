from django.urls import path
from .views import GetCardView, UpdateCollectionView, PingView


# URL patterns for the cards app
urlpatterns = [
    path('get_card/', GetCardView.as_view(), name='get-card'),
    path('update_collection/', UpdateCollectionView.as_view(), name='update-collection'),
    path('ping/', PingView.as_view(), name='ping')
]
