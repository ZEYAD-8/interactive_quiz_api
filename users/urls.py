from django.urls import path
from .views import RegisterUserView, LoginUserView, LogoutUserView, UserProfileView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('logout/', LogoutUserView.as_view(), name='logout_user'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]