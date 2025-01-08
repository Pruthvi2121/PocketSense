# myapp/urls.py
from django.urls import path
from .views import LoginView, SignUpView, UserProfileAPIView, LogoutAPIView

#  ProductAPIView, CustomerAPIView, OrderAPIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutAPIView.as_view()), 
    path('profile/', UserProfileAPIView.as_view()),

  
]


