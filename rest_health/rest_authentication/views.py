from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer
from .models import CustomUser
from .utils import send_otp
from django.core.cache import cache
from django.utils import timezone

class UserRegistrationView(APIView):
    """
    API view for registering users (patients and doctors).
    Users will receive an OTP, and only after OTP verification will the account be created.
    """
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Handles registration of a user and sends an OTP to the phone number.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            role = serializer.validated_data['role']
            phone_number = serializer.validated_data['phone_number']
            email = serializer.validated_data.get('email', None)

            # Check if user exists based on phone number for patients and doctors
            if role == 'patient' and CustomUser.objects.filter(phone_number=phone_number).exists():
                return Response({"detail": "A user with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            if role == 'doctor' and CustomUser.objects.filter(phone_number=phone_number).exists():
                return Response({"detail": "A doctor with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = send_otp(phone_number)


            new_user = CustomUser.objects.create(
                role=role,
                phone_number=phone_number,
                is_iranian=serializer.validated_data['is_iranian'],
                national_id=serializer.validated_data.get('national_id', None),
                passport_id=serializer.validated_data.get('passport_id', None),
                email=email,
                nezam_vazife_code=serializer.validated_data.get('nezam_vazife_code', None),
                is_verified=False,
            )
            new_user.save()

            return Response({"detail": "OTP sent to phone number. Please verify to complete registration."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated requests

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            return Response({"detail": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve OTP from the cache
        cached_otp = cache.get(f"otp_{phone_number}")

        if not cached_otp:
            return Response({"detail": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid, now we verify the user
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Clear the OTP from cache
        cache.delete(f"otp_{phone_number}")

        # Create JWT token for the user upon successful verification
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "detail": "User verified successfully.",
            "access_token": str(access_token),
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)