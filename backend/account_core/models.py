# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)  # Supports international formats
    #
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin Profile: {self.user.username}"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization_code = models.CharField(max_length=30, unique=True, null=True)  # Changed to `specialization_code` for clarity

    def __str__(self):
        return f"Doctor Profile: {self.user.username}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    national_code = models.CharField(max_length=30, unique=True, null=True, blank=True)  # Changed to `national_code` for clarity
    passport_number = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"Customer Profile: {self.user.username}"
