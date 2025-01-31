from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import CustomUser
from django.core.cache import cache

class OTPVerificationTest(APITestCase):
    
    def setUp(self):
        """Set up necessary objects for the test."""
        self.phone_number = "1234567890"
        self.role = "patient"
        self.is_iranian = True
        self.national_id = "3332323"
        
        self.user = CustomUser.objects.create(
        phone_number=self.phone_number,
        role=self.role,
        is_iranian=self.is_iranian,
        national_id=self.national_id,
        is_verified=False,
        )
        print(f"Created user: {self.user.phone_number}, Verified: {self.user.is_verified}")
        
    @patch('rest_authentication.views.send_otp')  # Patch the correct path
    def test_otp_send(self, mock_send_otp):
        """Test that OTP is sent successfully for an Iranian patient."""
        url = reverse('register')  # URL for registering and sending OTP

        # Mock the OTP sending function to return a dummy OTP
        mock_send_otp.return_value = "123456"

        # Make POST request to register user and send OTP
        data = {
            'phone_number': self.phone_number,
            'role': self.role,
            'is_iranian': self.is_iranian,
            'national_id': self.national_id,  # Required for Iranian patients
        }
        response = self.client.post(url, data, format='json')

        # Print the response data for debugging
        print("Response data:", response.data)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that OTP sending function was called
        mock_send_otp.assert_called_once_with(self.phone_number)
        
    def test_otp_verify_correct(self):
        """Test OTP verification with correct OTP."""
        # Send OTP (store in cache for this test)
        otp = "123456"
        cache.set(f"otp_{self.phone_number}", otp, timeout=300)

        # Debug: Check if OTP is stored in cache
        cached_otp = cache.get(f"otp_{self.phone_number}")
        print(f"Cached OTP: {cached_otp}")  # Should print "123456"

        # Make POST request to verify OTP
        url = reverse('otp-verification')  # Ensure this URL name is correct
        data = {'phone_number': self.phone_number, 'otp': otp}
        response = self.client.post(url, data, format='json')

        # Debug: Print the response data
        print("Response data:", response.data)

        # Check that OTP verification is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_otp_verify_incorrect(self):
        """Test OTP verification with incorrect OTP."""
        # Send OTP (store in cache for this test)
        otp = "123456"
        cache.set(f"otp_{self.phone_number}", otp, timeout=300)
        
        # Make POST request to verify OTP with incorrect OTP
        url = reverse('otp-verification')  # Ensure this URL name is correct
        response = self.client.post(url, {'phone_number': self.phone_number, 'otp': "wrongotp"})
        
        # Check that OTP verification fails with incorrect OTP
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Invalid OTP.")

    def test_otp_expiry(self):
        """Test that OTP expires after a certain period."""
        # Send OTP (store in cache for this test)
        otp = "123456"
        cache.set(f"otp_{self.phone_number}", otp, timeout=1)  # Timeout set to 1 second for testing
        
        # Wait for OTP to expire
        import time
        time.sleep(2)  # Sleep for 2 seconds, making OTP expired
        
        # Make POST request to verify expired OTP
        url = reverse('otp-verification')  # Ensure this URL name is correct
        response = self.client.post(url, {'phone_number': self.phone_number, 'otp': otp})
        
        # Check that OTP verification fails with expired OTP
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "OTP has expired.")
