import random
import string
from django.core.mail import send_mail  # You can use this for email or integrate SMS gateway
from django.core.cache import cache
from datetime import timedelta, timezone
from rest_authentication.models import CustomUser  # Import your CustomUser model
from django.utils import timezone

def generate_otp(length=6):
    """Generate a random OTP of given length."""
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp(phone_number):
    """
    Generate OTP and send it to the provided phone number.
    We don't check for user existence in the database yet since user will be created after OTP verification.
    """
    # Generate OTP
    otp = generate_otp()  # Implement OTP generation logic here
    otp_expiry = timezone.now() + timedelta(minutes=5)  # Set expiration time for the OTP

    # You could save this OTP temporarily in the cache or a temporary model for later verification
    cache.set(f"otp_{phone_number}", otp, timeout=300)  # Cache OTP for 5 minutes

    # Send OTP via SMS or another service
    send_sms(phone_number, f"Your OTP is {otp}")

    return otp

def verify_otp(phone_number, otp):
    """Verify the OTP entered by the user."""
    cached_otp = cache.get(f"otp_{phone_number}")
    
    # Check if OTP matches
    if cached_otp != otp:
        return False  # OTP is invalid
    
    # OTP is valid, create the user and clear the cached OTP
    user_data = {'phone_number': phone_number}  # Include any other necessary data like password, role, etc.
    user = CustomUser.objects.create(**user_data)

    # Clear the OTP after successful verification
    cache.delete(f"otp_{phone_number}")
    
    return True  # OTP verified and user crea

def send_sms(phone_number,code):
    print(code,'mowmow')