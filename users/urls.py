# myapp/urls.py
from django.urls import path
from .views import LoginView, SignUpView, ProfileAPIView, LogoutAPIView, ForgotPasswordView, ResetPasswordView, UserListAPIView

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
    path('profile/', ProfileAPIView.as_view()),
    path('forgot_password/', ForgotPasswordView.as_view()),
    path('reset_password/', ResetPasswordView.as_view()),
    path('users/', UserListAPIView.as_view()),

]


