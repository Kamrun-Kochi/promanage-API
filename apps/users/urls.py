from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserListView,
    ChangePasswordView,
    LogoutView
)

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    
    # JWT Tokens
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),
]
