import random
from django.core.cache import cache
from django.core.mail import send_mail
from datetime import datetime, timedelta

def generate_otp(identifier, otp_type='sms'):
    """
    Generate and cache a 6-digit OTP for the given identifier (phone number or email).
    If an OTP already exists and hasn't expired, it will be reused.
    """
    # Check if an OTP already exists in the cache for the identifier
    existing_otp = cache.get(identifier)
    if existing_otp:
        return existing_otp  # Reuse the existing OTP if it's still valid

    # Generate a new 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Cache the OTP with a 5-minute expiration time
    cache.set(identifier, otp, timeout=300)

    # Send OTP based on the type (SMS for phone number, email for email)
    if otp_type == 'sms':
        # Replace with actual SMS sending logic (use an SMS gateway like Twilio)
        print(f"Send OTP {otp} to phone number {identifier}")
    elif otp_type == 'email':
        # Send OTP via email
        send_mail(
            'Your OTP for Login/Registration',
            f'Your OTP is {otp}. It is valid for 5 minutes.',
            'no-reply@example.com',  # Sender email
            [identifier],  # Recipient email
            fail_silently=False,
        )

    return otp


def verify_otp(identifier, otp):
    """
    Verify if the provided OTP matches the cached OTP for the given identifier.
    """
    saved_otp = cache.get(identifier)
    if saved_otp is None:
        return False  # OTP expired or not generated

    # Check if the OTP matches
    if str(saved_otp) == str(otp):
        # OTP is valid; remove it from the cache to prevent reuse
        cache.delete(identifier)
        return True

    return False
