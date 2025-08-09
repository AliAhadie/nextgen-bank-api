import random
import string
from django.utils import timezone as timzone
from datetime import timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp


def generate_username()-> str:
    """Generate a unique username for a bank user."""
    prefix = 'BankUser-'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    username = prefix + suffix
    return username





def set_jwt_cookies(response, access_token, refresh_token):
    """Set JWT token in cookies."""
    response.set_cookie(
        expires=timzone.now() + timedelta(days=7),  # Cookie expiration time
        key='access_token',  # Name of the cookie
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax',  # Adjust as needed (Lax, Strict, None)
        
    )
    response.set_cookie(
        expires=timzone.now() + timedelta(days=7),  # Cookie expiration time
        key='refresh_token',  # Name of the cookie
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax',  # Adjust as needed (Lax, Strict, None)
        
    )
    return response


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT Authentication class to handle JWT tokens in cookies."""
    
    def authenticate(self, request):
        """Authenticate the user using JWT tokens from cookies."""
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not access_token and not refresh_token:
            return None
        
        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)
        
        return (user, validated_token) if user else None


