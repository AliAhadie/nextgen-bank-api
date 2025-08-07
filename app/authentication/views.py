from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateUserSerializer,BaseUserSerializer,ActivationAccountSerializer
from .models import User
from .tasks.task_email import send_activation_email
from django.core.cache import cache
from .models import AccountStatus

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
    serializer_class=ActivationAccountSerializer
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
