from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = PhoneNumberField(unique=True, null=False, blank=False)
    
    # Fields for patient authentication
    is_iranian = models.BooleanField(default=False)  # True if Iranian
    national_id = models.CharField(max_length=20, null=True, blank=True)  # For Iranian patients
    passport_id = models.CharField(max_length=50, null=True, blank=True)  # For non-Iranian patients
    email = models.EmailField(null=True, blank=True)  # For non-Iranian patients

    # Fields for doctor authentication
    nezam_vazife_code = models.CharField(max_length=50, null=True, blank=True)  # For doctors
    doctor_national_id = models.CharField(max_length=20, null=True, blank=True)  # For doctor ID verification

    def authenticate_patient(self):
        """Custom validation for patient authentication."""
        if self.is_iranian:
            return bool(self.phone_number and self.national_id)
        else:
            return bool(self.passport_id and self.email)

    def authenticate_doctor(self):
        if not self.nezam_vazife_code or not self.doctor_national_id or not self.phone_number:
            return False
        return True
