from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = CustomUser
        fields = ['password', 'role', 'phone_number', 'is_iranian', 'national_id', 
                  'passport_id', 'email', 'nezam_vazife_code']

    def validate(self, data):
        """Custom validation for patient or doctor registration."""

        # Debugging logs
        print(f"Validating data: {data}")

        if data['role'] == 'patient':
            # Debugging logs for patients
            print("Validating patient registration")
            
            # Foreign patient validation (if not Iranian)
            if not data.get('is_iranian', True):  # Foreign patient (is_iranian=False)
                print("Foreign patient")
                if data.get('phone_number'):
                    raise serializers.ValidationError("Foreign patients cannot provide a phone number.")
                else:
                    data['phone_number'] = f"non_ts{data.get('passport_id')}"  # Generate phone number based on passport_id

                if not data.get('passport_id') or not data.get('email'):
                    raise serializers.ValidationError("Foreign patients must provide both a passport ID and an email.")
            else:  # Iranian patient (is_iranian=True)
                print("Iranian patient")
                if not data.get('phone_number'):
                    raise serializers.ValidationError("Iranian patients must provide a phone number.")
                if not data.get('national_id'):
                    raise serializers.ValidationError("Iranian patients must provide a national ID.")

            # Assuming you have authentication logic for patients in the model
            user = CustomUser(**data)
            if not user.authenticate_patient():
                raise serializers.ValidationError("Invalid patient details.")

        elif data['role'] == 'doctor':
            # Debugging logs for doctors
            print("Validating doctor registration")
            
            if 'phone_number' not in data or not data['phone_number']:
                raise serializers.ValidationError({"phone_number": "Doctors must provide a valid phone number."})

            # Assuming you have authentication logic for doctors in the model
            user = CustomUser(**data)
            if not user.authenticate_doctor():
                raise serializers.ValidationError("Invalid doctor details.")


        
        return data
