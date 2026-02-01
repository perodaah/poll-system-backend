from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Poll, Option, Vote  
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    PollSerializer,
    PollListSerializer,
    VoteSerializer
)
from .permissions import IsOwnerOrReadOnly
from django.db.models import Count
from rest_framework.decorators import action 
import hashlib

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
    
    
    def get_voter_identifier(self, request):
        """
        Get unique identifier for the voter.
        - Authenticated users: use user ID
        - Anonymous users: use hashed IP address
        """
        if request.user.is_authenticated:
            return f"user-{request.user.id}"
        else:
            #Get client IP address from request
            ip = request.META.get('REMOTE_ADDR', '')
            # Hash the IP for privacy
            return f"ip-{hashlib.sha256(ip.encode()).hexdigest()}"
        
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def vote(self, request, pk=None):
        """
        Cast a vote on this poll 
        POST /api/polls/{id}/vote/
        Body: {"option_id": 2}
        """
        poll = self.get_object()
        
        # Check if poll is active
        if not poll.is_active:
            return Response(
                {"error": "This poll is no longer accepting vote."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if poll has expired
        if poll.is_expired():
            return Response(
                {"error": "This poll has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate the vote data
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        option_id = serializer.validated_data['option_id']
        
        # Verify option belongs to this poll
        try:
            option = Option.objects.get(id=option_id)
            if option.poll_id != poll.id:
                return Response(
                    {"error": "This option does not belong to this poll."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Option.DoesNotExist:
            return Response(
                {"error": "Invalid option."},
                status=status.HTTP_400_BAD_REQUEST
            )
        voter_identifier = self.get_voter_identifier(request)
        
        # Try to create the vote (duplicate will be caught by database constraint)
        try:
            vote = Vote.objects.create(
                poll=poll,
                option_id=option_id,
                voter_identifier=voter_identifier
            )
            
            return Response({
                "message": "Vote recorded successfully",
                "poll_id": poll.id,
                "option_id": option_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Check if it's a duplicate vote error
            if 'unique_vote_per_poll' in str(e):
                return Response(
                    {"error": "You have already voted on this poll."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "An error occurred while recording your vote."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def results(self, request, pk=None):

        """
        Get poll results with vote counts and percentages.
        
        GET /api/polls/{id}/results/
        """
        poll = self.get_object()
        
        # Get total votes for this poll
        total_votes = poll.votes.count()
        
        # Get vote count per option using aggregation
        options_with_votes = poll.options.annotate(
            vote_count=Count('votes')
        ).order_by('order_index')
        
        # Calculate percentages
        results = []
        for option in options_with_votes:
            percentage = (option.vote_count / total_votes * 100) if total_votes > 0 else 0
            results.append({
                "option": option.text,
                "votes": option.vote_count,
                "percentage": round(percentage, 2)
            })
        
        return Response({
            "poll": {
                "id": poll.id,
                "title": poll.title,
                "total_votes": total_votes,
                "is_active": poll.is_active,
                "is_expired": poll.is_expired()
            },
            "results": results
        }, status=status.HTTP_200_OK)