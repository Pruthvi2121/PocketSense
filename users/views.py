from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.contrib.auth import authenticate, logout
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserSignupSerializer, UserUpdateSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError, APIException
from django.db import transaction
import random
from django.utils import timezone
from common.functions import serailizer_errors, send_email 
from rest_framework.permissions import IsAuthenticated, AllowAny
from secrets import token_urlsafe
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.db.models import Q

logger = logging.getLogger(__name__)




@extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail':{'type': 'string', 'example':"OTP sent successfully! Please check your email for the email verification OTP. It has been sent to your account. Thank you!"},
                    'results': {
                        'type': 'object',
                        'properties':{
                            "id":{'type': 'integer'},
                            "email":{"type":"string", 'example':'user@example.com'}
                          }
                        },   
                }
            }
        }
    )
# user signup 
class SignUpView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            entered_otp = request.data.get('otp', None)

            if entered_otp != None:
                email = request.data.get('email', None)
                user = User.objects.get(email=email)
                if entered_otp==user.otp:
                    user.is_email_verified = True
                    user.save()
                    refresh = RefreshToken.for_user(user) 
                    access_token = str(refresh.access_token)

                    return Response({"detail": "Email OTP verified successfully.","access_token": access_token, "refresh_token": str(refresh),
                                      'results':{"id":user.id, "email":user.email}}, status=status.HTTP_200_OK) 
                else:
                    return Response({"detail": "Sorry, OTP didn't match"}, status=status.HTTP_400_BAD_REQUEST)

            else:  

                email = request.data.get('email', None)   
                          
                if User.objects.filter(email=email, is_email_verified=False).exists():
                    return Response({"detail": "User already exists but email is not verified. Please verify your email.", 'results':{ "email":email}}, status=422)
                

             
                # Handle new user signup
                serializer = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                password = make_password(serializer.validated_data['password'])
                serializer.validated_data['password'] = password
                serializer.validated_data['username'] = serializer.validated_data['email']
               
                user = serializer.save()
                
            
                otp = random.randint(100000, 999999)
                subject = f"Your Email Verification Code for Pocket Sense - {otp}"
            
                context = {'otp':otp, 'first_name':user.first_name, 'last_name': user.last_name }
               
                response = send_email(subject=subject,context=context, to_emails=[user.email], template_name='eamil_verification.html')
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()

                return Response({'detail': 'OTP sent successfully! Please check your email for the email verification OTP. It has been sent to your account. Thank you!',
                                    }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            return Response({'detail': f"{field_name.capitalize()} - {error_message}"}, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)






# user login
@extend_schema(
        request={
            "application/json":{
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string'}  
            },
        
        }},
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'},
                    'refresh_token': {'type': 'string'}
                }
            }
        }
    )
class LoginView(APIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email', None)
            password = request.data.get('password', None)
            
            if not email or not password:
                return Response({'detail': 'email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)    
            try:
                if (email):
                    user_account = User.objects.get(email=email)
                    
            except User.DoesNotExist:
                return Response({'detail': 'Account not found!'}, status=status.HTTP_404_NOT_FOUND)
                
            if user_account and not user_account.check_password(password):
                return Response({'detail': 'Incorrect password/email!.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user_account.is_email_verified == False:
                return Response({"detail": "User Email is not verified. Please verify your email."}, status=422)

            user = authenticate(username=user_account.email, password=password)
            
            refresh = RefreshToken.for_user(user) 
            access_token = str(refresh.access_token)

            return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            return Response({'detail': f"{field_name} - {error_message}"}, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)
    



# Log Out API View
class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK) 


class ProfileAPIView(APIView):
    permission_classes=[IsAuthenticated]   # Ensure the user is authenticated
    serializer_class = UserUpdateSerializer

    def get(self, request, tenant=None):
        try:
            user = request.user   # Retrieve the currently authenticated user
            serializer = UserUpdateSerializer(user)  # Serialize the user's data to return it as JSON
            return Response({"results": serializer.data})    # Return the serialized data in the respons
        
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)
        
    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail':{'type': 'string','example':'Profile Updated Successfully'},
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'detail':{'type': 'string'},
                }
            }
        }
    )
    def put(self, request,  tenant=None):
        try:
            user = request.user  # Get the current authenticated user
            
            # Use partial=True to allow updating only specified fields
            serializer = UserUpdateSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True) # Validate the data and raise errors if the data is invalid

            # Save the validated data to update the user profile
            serializer.save()
            return Response({"detail": "Profile Updated Successfully", "results":serializer.data}, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            if "_" in field_name:
                field_name = " ".join(word.capitalize() for word in field_name.split("_"))
            else:
                field_name = field_name.capitalize()
            return Response({'detail': f"{field_name} - {error_message}"}, status=status.HTTP_400_BAD_REQUEST) 
        


# Forgot Password
@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type':
                    'string',
                    'example':
                    'Reset password link is send to your email. Please check your inbox.'
                },
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'User not found'
                },
            }
        }
})
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny] # Allow unauthenticated users to access this endpoint
    serializer_class = ForgotPasswordSerializer

    def post(self, request, tenant=None):
        try:
            email = request.data.get('email')  # Extract email from the request data

            if email:
                user = User.objects.get(email=email) # Retrieve the user associated with the provided email

                # Generate a secure token and save it to the user for validation in the reset process
                token = token_urlsafe(16)
                user.token_created_at = timezone.now()
                user.token = token

                # Send a password reset email with the token and user information
                response = send_email(
                    subject='Password Reset Pocket Sense',
                    context={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'reset_password_link': f'{settings.BASE_FRONTEND_URL}/reset-password/?email={user.email}&token={user.token}',
                    },
                    template_name='forgot_password.html',
                    to_emails=[user.email]

                )

                if response:
                    # Save the user’s token and token creation time
                    user.save()
                    return Response(
                        {
                            'detail':
                            'Reset password link is send to your email. Please check your inbox.'
                        },
                        status=status.HTTP_200_OK)
                else: 
                     # Return error if email could not be sent
                    return Response(
                        {'detail': 'Email sending failed, please try again!'},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                # Inform the user that an email address is required
                return Response({'detail': 'Please enter valid email address'},
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)


# Reset Password using reset_token
@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Password reset successfully.'
                },
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'Password and Confirm Password do not match'
                },
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'example': 'User not found.'
                },
            }
        }
    })
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to access this endpoint
    serializer_class = ResetPasswordSerializer

    def post(self, request, tenant=None): 
        serializer = self.serializer_class(data=request.data) # Initialize serializer
        try:
            # Extract email and token from the request data
            email = request.data.get('email')
            token = request.data.get('token')
            
            # Retrieve the user associated with the provided email
            user = User.objects.get(email=email)
            
            if not user.token_is_valid():  # Check if the token is still valid; if not, return an expiration error
                return Response(
                    {'detail': 'Password Reset Link has expired, Try again!.'},
                    status=status.HTTP_400_BAD_REQUEST)
            
            # Validate the token; if it doesn't match, return an invalid token error
            if token != user.token :
                return Response({'detail': 'Invalid token'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.is_valid(raise_exception=True)  # Validate incoming data, raising any validation errors

            # Extract validated email, token, and password fields from the serializer
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']

            # Update the user’s password with the new one
            user.set_password(password)
            user.save()

            return Response({'detail': 'Password reset successfully.'},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            field_name, error_message = serailizer_errors(e)
            if field_name == 'non_field_errors':
                return Response({'detail': f"{error_message}"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {'detail': f"{field_name.capitalize()} - {error_message}"},
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            logger.info("Something went wrong", exc_info=ex)
            raise APIException(detail=ex)



class UserListAPIView(APIView):
  
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)
        users = User.objects.all()

        if search_query:
            users = users.filter(
                Q(email__icontains=search_query) | 
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) 
               
            )
        
        serializer = UserSerializer(users, many=True)
     
        return Response({"results":serializer.data},status=status.HTTP_200_OK)