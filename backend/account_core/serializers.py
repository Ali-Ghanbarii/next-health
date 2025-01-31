from rest_framework import serializers
from .models import User, AdminProfile, DoctorProfile, CustomerProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone_number']


class LoginOrRegisterSerializer(serializers.Serializer):
    nationality = serializers.ChoiceField(choices=['iranian', 'foreign'])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    na_code = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    whole_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        nationality = data.get('nationality')

        if nationality == 'iranian':
            if not data.get('phone_number'):
                raise serializers.ValidationError("Phone number is required for Iranian users.")
            if not data.get('na_code'):
                raise serializers.ValidationError("NA code is required for Iranian users.")
        elif nationality == 'foreign':
            if not data.get('email'):
                raise serializers.ValidationError("Email is required for foreign users.")
            if not data.get('whole_name'):
                raise serializers.ValidationError("Full name is required for foreign users.")
        return data