from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/auth/register/
    Body: {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepassword123",
        "password2": "securepassword123"
    }
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]  # Anyone can register
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "user": UserSerializer(user).data,
            "message": "User registered successfully. Please login to get your tokens."
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveAPIView):
    """
    API endpoint to get current user's profile.
    
    GET /api/auth/profile/
    Requires: Authorization header with Bearer token
    """
    permission_classes = [permissions.IsAuthenticated]  # Must be logged in
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user  # Return the logged-in user