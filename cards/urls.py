from django.urls import path
from .views import CardNameView, PingView


# URL patterns for the cards app
urlpatterns = [
    path('card/', CardNameView.as_view(), name='card-name'),
    path('ping/', PingView.as_view(), name='ping')
]
