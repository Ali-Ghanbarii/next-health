from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)  # Make phone_number optional

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'role', 'phone_number', 'is_iranian', 'national_id', 
                  'passport_id', 'email', 'nezam_vazife_code', 'doctor_national_id']

    def validate(self, data):
        """Custom validation for patient or doctor registration."""
    
        if data['role'] == 'patient':
            if not data.get('is_iranian', True):  # Foreign patient (is_iranian=False)
                if data.get('phone_number'):
                    raise serializers.ValidationError("Foreign patients cannot provide a phone number.")
                else:
                    data['phone_number'] = f"non_ts{data.get('passport_id')}" 

                if not data.get('passport_id') or not data.get('email'):
                    raise serializers.ValidationError("Foreign patients must provide both a passport ID and an email.")
            else:  # Iranian patient (is_iranian=True)
                if not data.get('phone_number'):
                    raise serializers.ValidationError("Iranian patients must provide a phone number.")
                if not data.get('national_id'):
                    raise serializers.ValidationError("Iranian patients must provide a national ID.")

            user = CustomUser(**data)
            if not user.authenticate_patient():
                raise serializers.ValidationError("Invalid patient details.")

        elif data['role'] == 'doctor':
            if 'phone_number' not in data or not data['phone_number']:
                raise serializers.ValidationError({"phone_number": "Doctors must provide a valid phone number."})

            user = CustomUser(**data)
            if not user.authenticate_doctor():
                raise serializers.ValidationError("Invalid doctor details.")

        return data

