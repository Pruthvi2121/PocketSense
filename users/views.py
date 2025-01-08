from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from django.contrib.auth.hashers import make_password



logger = logging.getLogger(__name__)

# user signup 
class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data['password'])
            serializer.validated_data['password'] = password
            user = serializer.save()
            return Response({'detail': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# user login
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'detail': 'username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            if (username):
                user_account = User.objects.get(username=username)
                
        except User.DoesNotExist:
            return Response({'detail': 'Account not found!'}, status=status.HTTP_404_NOT_FOUND)
             
        if user_account and not user_account.check_password(password):
            return Response({'detail': 'Incorrect password/username!.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user_account.username, password=password)
        refresh = RefreshToken.for_user(user) 
        access_token = str(refresh.access_token)

        return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)
    

# Log Out API View
class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK) 

# User Profile
class UserProfileAPIView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({"results": serializer.data})
