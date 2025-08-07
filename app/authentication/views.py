from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateUserSerializer,BaseUserSerializer
from .models import User

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
               
