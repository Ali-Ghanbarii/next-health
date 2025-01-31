from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, role, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone number must be set")
        user = self.model(phone_number=phone_number, role=role, **extra_fields)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, role, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, role, **extra_fields)
    

class CustomUser(AbstractBaseUser):
    ROLES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLES)
    national_id = models.CharField(max_length=10, blank=True, null=True)  # This field should exist
    passport_id = models.CharField(max_length=20, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_iranian = models.BooleanField(default=False)
    nezam_vazife_code = models.CharField(max_length=50, blank=True, null=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return self.phone_number

    def get_short_name(self):
        return self.phone_number

    def authenticate_patient(self):
        """Custom validation for patient authentication."""
        if self.is_iranian:
            return bool(self.phone_number and self.national_id)
        else:
            return bool(self.passport_id and self.email)

    def authenticate_doctor(self):
        """Custom validation for doctor authentication."""
        return bool(self.nezam_vazife_code and self.phone_number and self.national_id)

