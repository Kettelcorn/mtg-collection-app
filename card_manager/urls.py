from django.urls import path
from .views.user_views import CreateUserView, GetUsersView, ChangeUsernameView, DeleteUserView
from .views.collection_views import (CreateCollectionView, GetCollectionView, GetCollectionsView,
                                     UpdateCollectionView, DeleteCollectionView)
from .views.card_views import GetCardView
from .views.utility_views import PingView, OAuthCallbackView, StartOAuthView, FetchTokensView, CustomTokenRefreshView


# URL patterns for the card_manager app
urlpatterns = [
    # User views
    path('create_user/', CreateUserView.as_view(), name='create-user'),
    path('get_users/', GetUsersView.as_view(), name='get-users'),
    path('change_username/', ChangeUsernameView.as_view(), name='change-username'),
    path('delete_user/', DeleteUserView.as_view(), name='delete-user'),

    # Collection views
    path('create_collection/', CreateCollectionView.as_view(), name='create-collection'),
    path('get_collection/', GetCollectionView.as_view(), name='get-collection'),
    path('get_collections/', GetCollectionsView.as_view(), name='get-collection'),
    path('update_collection/', UpdateCollectionView.as_view(), name='update-collection'),
    path('delete_collection/', DeleteCollectionView.as_view(), name='delete-collection'),

    # Card views
    path('get_card/', GetCardView.as_view(), name='get-card'),

    # Utility views
    path('ping/', PingView.as_view(), name='ping'),
    path('oauth_callback/', OAuthCallbackView.as_view(), name='oauth-callback'),
    path('start_oauth/', StartOAuthView.as_view(), name='start-oauth'),
    path('fetch_tokens/', FetchTokensView.as_view(), name='fetch-tokens'),
    path('token_refresh/', CustomTokenRefreshView.as_view(), name='token-refresh')
]
