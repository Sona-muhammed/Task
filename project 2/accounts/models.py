import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    """
    Custom user model that uses email as the unique identifier
    instead of username.
    """
    email = models.EmailField(_('email address'), unique=True)
    is_verified = models.BooleanField(default=False)  # Add email verification field
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class OTPVerification(models.Model):
    """
    Model to store OTP codes for email verification.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp_codes')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.email} - {self.otp_code}'
    
    def is_expired(self):
        """Check if OTP has expired (after 10 minutes)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP code"""
        return str(random.randint(100000, 999999))