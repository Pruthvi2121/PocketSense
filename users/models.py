from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from common.models import BaseModel
from datetime import timedelta
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("username", email)  # Set username to email

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    


class User(AbstractUser, BaseModel):

    email = models.EmailField(unique=True) 
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lastlogin = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    token = models.CharField(max_length=36, null=True, blank=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    

    objects = CustomUserManager()

    class Meta:
        ordering = ['id']

    def token_is_valid(self):
        if not self.token_created_at:
            return False
        expiration_time = timedelta(minutes=10)
        return (timezone.now() - self.token_created_at) <= expiration_time
    