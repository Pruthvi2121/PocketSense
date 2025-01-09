from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'date_of_birth')
        extra_kwargs = {'password': {'write_only': True}}
    
    


    def validate_password(self, value):
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        

        return value

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'date_of_birth')
        extra_kwargs = {'password': {'write_only': True}}



class UserUpdateSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = User
        fields = ['id', 'first_name',  'last_name', 'profile_pic',  'date_of_birth']
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(max_length=36)
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "must be at least 8 characters long.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "must contain at least one special character.")

        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "must contain at least one lowercase letter.")

        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                "must contain at least one number.")

        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "Password and Confirm Password do not match.")
        return data