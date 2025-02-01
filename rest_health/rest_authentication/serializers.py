from rest_framework import serializers
from .models import CustomUser
from django.db.models import Q

class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    national_id = serializers.CharField(required=False, allow_blank=True)
    passport_id = serializers.CharField(required=False, allow_blank=True)
    nezam_vazife_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'role', 'phone_number', 'is_iranian', 'national_id', 
                  'passport_id', 'email', 'nezam_vazife_code']

    def validate(self, data):
        """Custom validation for patient or doctor registration."""
        print(f"Validating data: {data}")  # Debugging log

        role = data.get('role')
        phone_number = data.get('phone_number')
        is_iranian = data.get('is_iranian', True)
        national_id = data.get('national_id')
        passport_id = data.get('passport_id')
        email = data.get('email')
        nezam_vazife_code = data.get('nezam_vazife_code')

        # Ensure at least one unique identifier is provided
        if not phone_number and not email:
            raise serializers.ValidationError("Either phone number or email is required.")

        # Check if the user already exists based on role and provided identifiers
        user_exists = CustomUser.objects.filter(
        (Q(phone_number=phone_number) if phone_number else Q()) |
        (Q(email=email) if email else Q()) |
        (Q(national_id=national_id) if national_id else Q()) |
        (Q(passport_id=passport_id) if passport_id else Q()),
        role=role
        ).exists()
        
        if user_exists:
            print("User already exists. Proceeding to login.")
            return data

        # Patient validation
        if role == 'patient':
            if not is_iranian:  # Foreign patient
                if phone_number:
                    raise serializers.ValidationError("Foreign patients cannot provide a phone number.")
                if not passport_id or not email:
                    raise serializers.ValidationError("Foreign patients must provide both a passport ID and an email.")
                data['phone_number'] = f"non_ts{passport_id}"  # Generate phone number based on passport_id
            else:  # Iranian patient
                if not phone_number:
                    raise serializers.ValidationError("Iranian patients must provide a phone number.")
                if not national_id:
                    raise serializers.ValidationError("Iranian patients must provide a national ID.")

            user = CustomUser(**data)
            if not user.authenticate_patient():
                raise serializers.ValidationError("Invalid patient details.")

        # Doctor validation
        elif role == 'doctor':
            if is_iranian:
                if not phone_number or not national_id or not nezam_vazife_code:
                    raise serializers.ValidationError("Iranian doctors must provide phone number, national ID, and Nezam Vazife code.")
            else:
                if not passport_id or not email:
                    raise serializers.ValidationError("Foreign doctors must provide both a passport ID and an email.")

            user = CustomUser(**data)
            if not user.authenticate_doctor():
                raise serializers.ValidationError("Invalid doctor details.")

        return data
