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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

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
    ViewSet for managing polls.
    
    Provides CRUD operations for polls and custom actions for voting and viewing results.
    """
    queryset = Poll.objects.filter(is_active=True).select_related('created_by').prefetch_related('options')
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PollListSerializer
        return PollSerializer

    def perform_create(self, serializer):
        """ 
        Automatically set the poll creator to the logged-in user
        """
        serializer.save(created_by=self.request.user)
        
    def get_queryset(self):
        """
        Optionally filter by active status via query param.
        For vote and results actions, show all polls (including inactive).
        """
        queryset = Poll.objects.select_related('created_by').prefetch_related('options')
        
        if self.action in ['vote', 'results']:
            return queryset.order_by('-created_at')
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
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
            ip = request.META.get('REMOTE_ADDR', '')
            return f"ip-{hashlib.sha256(ip.encode()).hexdigest()}"
    
    @extend_schema(
        summary="Cast a vote on a poll",
        description="Submit a vote for a specific option in the poll. Works for both authenticated and anonymous users. Duplicate votes are prevented.",
        request=VoteSerializer,
        responses={
            201: OpenApiExample(
                'Success',
                value={
                    "message": "Vote recorded successfully",
                    "poll_id": 1,
                    "option_id": 2
                }
            ),
            400: OpenApiExample(
                'Duplicate Vote',
                value={"error": "You have already voted on this poll."}
            )
        },
        tags=['Voting']
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def vote(self, request, pk=None):
        """
        Cast a vote on this poll.
        
        POST /api/polls/{id}/vote/
        Body: {"option_id": 2}
        """
        poll = self.get_object()
        
        if not poll.is_active:
            return Response(
                {"error": "This poll is no longer accepting votes."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if poll.is_expired():
            return Response(
                {"error": "This poll has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        option_id = serializer.validated_data['option_id']
        
        try:
            option = Option.objects.get(id=option_id, poll=poll)
        except Option.DoesNotExist:
            return Response(
                {"error": "This option does not belong to this poll."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        voter_identifier = self.get_voter_identifier(request)
        
        try:
            vote = Vote.objects.create(
                poll=poll,
                option=option,
                voter_identifier=voter_identifier
            )
            
            return Response({
                "message": "Vote recorded successfully",
                "poll_id": poll.id,
                "option_id": option_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_str = str(e)
            if 'unique_vote_per_poll' in error_str or 'UNIQUE constraint' in error_str:
                return Response(
                    {"error": "You have already voted on this poll."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                print(f"Vote creation error: {e}")
                return Response(
                    {"error": "An error occurred while recording your vote."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @extend_schema(
        summary="Get poll results",
        description="Retrieve vote counts and percentages for all options in the poll. Available to everyone, even for inactive polls.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "poll": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "string"},
                            "total_votes": {"type": "integer"},
                            "is_active": {"type": "boolean"},
                            "is_expired": {"type": "boolean"}
                        }
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "option": {"type": "string"},
                                "votes": {"type": "integer"},
                                "percentage": {"type": "number"}
                            }
                        }
                    }
                }
            }
        },
        tags=['Voting']
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def results(self, request, pk=None):
        """
        Get poll results with vote counts and percentages.
        
        GET /api/polls/{id}/results/
        """
        poll = self.get_object()
        
        total_votes = poll.votes.count()
        
        options_with_votes = poll.options.annotate(
            vote_count=Count('votes')
        ).order_by('order_index')
        
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