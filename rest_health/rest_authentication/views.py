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

        # Determine the identifier (phone number or email)
        identifier = phone_number if is_iranian else email

        if not identifier:
            return Response({"detail": "Phone number or email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        try:
            if is_iranian:
                user = CustomUser.objects.get(phone_number=phone_number, role=role)
            else:
                user = CustomUser.objects.get(email=email, role=role)
            
            # If user exists, log them in by generating JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                "detail": "User logged in successfully.",
                "access_token": str(access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            # If user does not exist, proceed with OTP generation
            otp = send_otp(identifier)

            # Store the OTP and user data in the cache
            cache.set(f"otp_{identifier}", otp, timeout=300)  # OTP expires in 5 minutes
            cache.set(f"user_data_{identifier}", serializer.validated_data, timeout=300)  # User data expires in 5 minutes

            return Response({
                "detail": f"OTP sent to {identifier}. Please verify to complete registration.",
                "identifier": identifier  # Return the identifier to the client
            }, status=status.HTTP_201_CREATED)



class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        identifier = request.data.get('identifier')  # Get the identifier from the request

        if not otp or not identifier:
            return Response({"detail": "OTP and identifier are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve OTP and user data from the cache
        cached_otp = cache.get(f"otp_{identifier}")
        user_data = cache.get(f"user_data_{identifier}")

        if not cached_otp or not user_data:
            return Response({"detail": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid, now we create the user
        try:
            # Create a new user
            new_user = CustomUser.objects.create(
                role=user_data['role'],
                phone_number=user_data.get('phone_number'),
                is_iranian=user_data.get('is_iranian', True),
                national_id=user_data.get('national_id', None),
                passport_id=user_data.get('passport_id', None),
                email=user_data.get('email'),
                nezam_vazife_code=user_data.get('nezam_vazife_code', None),
                is_verified=True,  # Mark user as verified
            )
            new_user.save()

            # Clear the OTP and user data from the cache
            cache.delete(f"otp_{identifier}")
            cache.delete(f"user_data_{identifier}")

            # Create JWT token for the user upon successful verification
            refresh = RefreshToken.for_user(new_user)
            access_token = refresh.access_token

            return Response({
                "detail": "User verified and created successfully.",
                "access_token": str(access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)