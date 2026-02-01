from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Poll, Option, Vote  
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    PollSerializer,
    PollListSerializer
)
from .permissions import IsOwnerOrReadOnly

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
    
    
class PollViewSet(viewsets.ModelViewSet):
    """
    API endpoints for poll management.
    
    Provides:
    - GET /api/polls/ - List all active polls
    - POST /api/polls/ - Create new poll (authenticated users only)
    - GET /api/polls/{id}/ - Get poll details
    - PUT/PATCH /api/polls/{id}/ - Update poll (owner only)
    - DELETE /api/polls/{id}/ - Delete poll (owner only)
    """
    queryset = Poll.objects.filter(is_active=True).select_related('created_by').prefetch_related('options')
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PollListSerializer  # Use lightweight serializer for list view
        return PollSerializer  # Full serializer for detail view and others

    def perform_create(self, serializer):
        """ 
        Automatically set the poll creator to the logged-in user
        """
        serializer.save(created_by=self.request.user)
        
    def get_queryset(self):
        """
        Optionally filter by active status via query param.
        """
        queryset = Poll.objects.select_related('created_by').prefetch_related('options')
        
        # Filter by is_active if provided in query params
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            # By default, only show active polls
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')
