from django.urls import path
from .views import GetCardView, PingView


# URL patterns for the cards app
urlpatterns = [
    path('get_card/', GetCardView.as_view(), name='get-card'),
    path('ping/', PingView.as_view(), name='ping')
]
