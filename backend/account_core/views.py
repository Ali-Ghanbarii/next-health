from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import LoginOrRegisterSerializer
from .utils import generate_otp, verify_otp
from proj_core import settings
from .models import CustomerProfile

User = get_user_model()


class LoginOrRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginOrRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            nationality = data['nationality']
            print(f"Session Key in Login/Register: {request.session.session_key}")
            if nationality == 'iranian':
                phone_number = data['phone_number']
                na_code = data['na_code']

                # Store registration data in session
                request.session['registration_data'] = {
                    'nationality': nationality,
                    'phone_number': phone_number,
                    'na_code': na_code,
                    'user_type': 'customer',
                }

                print(f"Stored session data: {request.session['registration_data']}")  # Debugging

            else:  # Non-Iranian (foreign)
                email = data['email']
                whole_name = data['whole_name']

                # Store registration data in session
                request.session['registration_data'] = {
                    'nationality': nationality,
                    'email': email,
                    'whole_name': whole_name,
                    'user_type': 'customer',
                }

                print(f"Stored session data: {request.session['registration_data']}")  # Debugging

            # Generate and send OTP
            identifier = phone_number if nationality == 'iranian' else email
            otp_type = 'sms' if nationality == 'iranian' else 'email'
            otp = generate_otp(identifier, otp_type=otp_type)

            if otp:
                return Response({'message': 'OTP sent successfully.', 'identifier': identifier}, status=status.HTTP_200_OK)
            return Response({'error': 'Failed to send OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        otp = request.data.get('otp')
        print(f"Session Key in OTP Verify: {request.session.session_key}")

        if not identifier or not otp:
            return Response({'error': 'Identifier and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if verify_otp(identifier, otp):
            registration_data = request.session.pop('registration_data', None)
            
            print(registration_data)
            
            if not registration_data:
                return Response({'error': 'No registration data found.'}, status=status.HTTP_400_BAD_REQUEST)

            # Debugging: Print the session data
            print(f"Registration data: {registration_data}") 

            # Create or retrieve the user
            user, created = User.objects.get_or_create(
                phone_number=registration_data.get('phone_number'),
                email=registration_data.get('email'),
                defaults={
                    'username': registration_data.get('phone_number') or registration_data.get('email'),
                    'user_type': registration_data.get('user_type'),
                },
            )

            # Create the customer profile if it doesn't exist
            if created or not hasattr(user, 'customer_profile'):
                if registration_data['nationality'] == 'iranian':
                    user.customer_profile = CustomerProfile.objects.create(
                        user=user,
                        national_code=registration_data['na_code']
                    )
                else:
                    user.customer_profile = CustomerProfile.objects.create(
                        user=user,
                        passport_number=registration_data['whole_name'],
                        email=registration_data['email']
                    )
                user.save()

            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class OTPGenerateView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        otp_type = request.data.get('otp_type', 'sms')  # Default to 'sms'
        if not identifier:
            return Response({'error': 'Identifier is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp(identifier, otp_type)
        return Response({'message': 'OTP sent successfully.', 'otp': otp if settings.DEBUG else None})

