from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateUserSerializer,BaseUserSerializer,ActivationAccountSerializer,LoginSerializer
from .models import User
from .tasks.task_email import send_activation_email,send_otp_email
from django.core.cache import cache
from .models import AccountStatus
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import OtpSerializer
from .utils import set_jwt_cookies

# Create your views here.

class UserCreateView(APIView):
    """
    View to handle user creation.
    """
    serializer_class = CreateUserSerializer
    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_activation_email.apply_async(args=[user.id])

            return Response({
                "message": "User created successfully",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    """
    View to handle user details retrieval.
    """
    def get(self, request):
        try:
            users=User.objects.all()
            serializer = BaseUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
               
class ActivationAccountView(APIView):
    """View to handle user account activation email sending."""
    serializer_class = ActivationAccountSerializer
    COOLDOWN_SECONDS = 120  # 2 دقیقه

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            cache_key = f"activation_email_sent_{user.id}"
            if cache.get(cache_key):
                return Response({
                    "error": "Activation email already sent recently. Please wait a few minutes."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            send_activation_email.apply_async(args=[user.id])
            cache.set(cache_key, True, timeout=self.COOLDOWN_SECONDS)

            return Response({
                "message": "Activation email sent successfully",
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ActivatedView(APIView):
    """View to handle user account activation."""
    def get(self,request,uuid):
        try:
            user=User.objects.filter(id=uuid).first()
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        print(user.account_status)

        user.account_status=AccountStatus.ACTIVE
        user.save()
        return Response({
                "message": "Acount is activate",
                "user_id": user.id
            }, status=status.HTTP_200_OK)



class UserLoginView(APIView):
    """View to handle user login and OTP generation."""
    serializer_class = LoginSerializer
    def post(self,request):
        serilaizer=self.serializer_class(data=request.data)
        if serilaizer.is_valid():
            email=serilaizer.validated_data.get('email')
            password=serilaizer.validated_data.get('password')
            try:
                user = authenticate(request, email=email, password=password)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)  
            if not user.is_active:
                return Response({"error": "User account is not active"}, status=status.HTTP_403_FORBIDDEN)
            # Generate OTP and send it to the user
            user.set_otp()
            user.save()
            send_otp_email.apply_async(args=[user.email, user.otp])
            return Response({
                'messsage': 'OTP sent to your email',
                'user_id': user.id
            }, status=status.HTTP_200_OK)   
        return Response(serilaizer.errors, status=status.HTTP_400_BAD_REQUEST)

               
class VerifyOtpView(APIView):
    serializer_class = OtpSerializer
    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user=User.objects.filter(otp=serializer.validated_data.get('otp')).first()
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if user is None:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            if not user.verify_otp(serializer.validated_data.get('otp')):
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            # Generate JWT tokens
            accsess_token=AccessToken.for_user(user)
            refresh_token=RefreshToken.for_user(user)
            response=Response({
                "message": "OTP verified successfully",
                "access_token": str(accsess_token),
                "refresh_token": str(refresh_token),
                "user_id": user.id
            }, status=status.HTTP_200_OK)
            set_jwt_cookies(response, accsess_token, refresh_token)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    """View to handle user logout by clearing JWT cookies."""
    def delete(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response