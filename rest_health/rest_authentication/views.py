from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response,Serializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer
from .models import CustomUser
from .utils import send_otp
from django.core.cache import cache
from django.utils import timezone

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data.get('phone_number')
        role = serializer.validated_data['role']
        is_iranian = serializer.validated_data.get('is_iranian', True)
        email = serializer.validated_data.get('email')

        # Determine the identifier (phone number for Iranian, email for non-Iranian)
        identifier = phone_number if is_iranian else email
        if not identifier:
            return Response({"detail": "Phone number or email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        if is_iranian:
            user = CustomUser.objects.filter(phone_number=phone_number, role=role).first()
        else:
            user = CustomUser.objects.filter(email=email, role=role).first()

        # Generate OTP regardless of user existence
        otp = send_otp(identifier)
        cache.set(f"otp_{identifier}", otp, timeout=300)  # OTP expires in 5 minutes

        # If the user exists, store a flag and user id for login.
        # Otherwise, store the validated data for new registration.
        if user:
            cache.set(f"user_data_{identifier}", {"existing": True, "user_id": user.id}, timeout=300)
            detail_msg = f"OTP sent to {identifier} for login. Please verify to continue."
        else:
            cache.set(f"user_data_{identifier}", serializer.validated_data, timeout=300)
            detail_msg = f"OTP sent to {identifier}. Please verify to complete registration."

        return Response({
            "detail": detail_msg,
            "identifier": identifier
        }, status=status.HTTP_201_CREATED)



class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        identifier = request.data.get('identifier')  # Get the identifier from the request

        if not otp or not identifier:
            return Response({"detail": "OTP and identifier are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve OTP and associated data from the cache
        cached_otp = cache.get(f"otp_{identifier}")
        user_data = cache.get(f"user_data_{identifier}")

        if not cached_otp or not user_data:
            return Response({"detail": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid. Check if this is a login for an existing user or a new registration.
        try:
            if isinstance(user_data, dict) and user_data.get("existing"):
                # Existing user: retrieve the user and log them in.
                user = CustomUser.objects.get(id=user_data.get("user_id"))
                detail_msg = "User logged in successfully."
            else:
                # New user: create the user from the validated data.
                user = CustomUser.objects.create(
                    role=user_data['role'],
                    phone_number=user_data.get('phone_number'),
                    is_iranian=user_data.get('is_iranian', True),
                    national_id=user_data.get('national_id', None),
                    passport_id=user_data.get('passport_id', None),
                    email=user_data.get('email'),
                    nezam_vazife_code=user_data.get('nezam_vazife_code', None),
                    is_verified=True,  # Mark user as verified after OTP confirmation
                )
                user.save()
                detail_msg = "User verified and created successfully."

            # Clear the OTP and user data from the cache
            cache.delete(f"otp_{identifier}")
            cache.delete(f"user_data_{identifier}")

            # Generate JWT tokens for the user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                "detail": detail_msg,
                "access_token": str(access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)