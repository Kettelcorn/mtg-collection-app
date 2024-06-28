from django.urls import path
from .views.user_views import GetUsersView, ChangeUsernameView, DeleteUserView, CreateUserView
from .views.collection_views import GetCollectionView, UpdateCollectionView
from .views.card_views import GetCardView
from .views.utility_views import PingView


# URL patterns for the card_manager app
urlpatterns = [
    # User views
    path('create_user/', CreateUserView.as_view(), name='create-user'),
    path('get_users/', GetUsersView.as_view(), name='get-users'),
    path('change_username/', ChangeUsernameView.as_view(), name='change-username'),
    path('delete_user/', DeleteUserView.as_view(), name='delete-user'),

    # Collection views
    path('get_collection/', GetCollectionView.as_view(), name='get-collection'),
    path('update_collection/', UpdateCollectionView.as_view(), name='update-collection'),

    # Card views
    path('get_card/', GetCardView.as_view(), name='get-card'),

    # Utility views
    path('ping/', PingView.as_view(), name='ping')
]
