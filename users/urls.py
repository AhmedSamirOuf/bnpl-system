from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserRegistrationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
]
