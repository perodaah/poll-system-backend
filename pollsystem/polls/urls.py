from django.urls import path
from .views import UserRegistrationView, UserProfileView

urlpatterns = [
    #Aunthentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
]