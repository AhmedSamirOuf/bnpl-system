from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path('user/register/', UserRegistrationView.as_view(), name='register'),
    path('user/login/', CustomTokenObtainPairView.as_view(), name='login'),
]