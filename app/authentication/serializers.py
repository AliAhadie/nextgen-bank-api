from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
User = get_user_model()
class BaseUserSerializer(serializers.ModelSerializer):
    """Base serializer for the User model."""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff','id_no')
        read_only_fields = ('id', 'is_active', 'is_staff')

class CreateUserSerializer(BaseUserSerializer):
    """Serializer for creating a new user."""
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)
    security_question = serializers.CharField(required=True)
    security_answer = serializers.CharField(required=True)

    def validate_password(self, attrs):
        """Validate the password strength."""
        if len(attrs) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in attrs):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in attrs):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in '!@#$%^&*()_+' for char in attrs):
            raise serializers.ValidationError("Password must contain at least one special character.")
        if attrs != self.initial_data.get('re_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create and return a new user."""
        validated_data.pop('re_password', None)
        user = User.objects.create_user(**validated_data)
       
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('password', 'security_question', 'security_answer','re_password')


class ActivationAccountSerializer(serializers.Serializer):
    email=serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        if not user.check_password(password):
            raise ValidationError("Incorrect password.")
        if not user.is_active:
            raise ValidationError("User account is not active.")
        return attrs
    
    def validate_password(self, attrs):
        """Validate the password strength."""
        if len(attrs) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in attrs):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in attrs):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in '!@#$%^&*()_+' for char in attrs):
            raise serializers.ValidationError("Password must contain at least one special character.")
        if attrs != self.initial_data.get('re_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs


class OtpSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    otp =serializers.CharField(max_length=6, min_length=6, required=True)

    def validate_otp(self, value):
        """Validate the OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value