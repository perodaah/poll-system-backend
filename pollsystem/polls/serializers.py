from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Poll, Option, Vote
from django.utils import timezone


class OptionSerializer(serializers.ModelSerializer):
    """ 
    Serializer for poll options.
    Used for nested creation and display
    """
    votes_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Option
        fields = ['id', 'text', 'order_index', 'votes_count']
        read_only_fields = ['id', 'votes_count']
        
    def get_votes_count(self, obj):
        """Get vote count for this option."""
        return obj.votes.count()
    
class PollSerializer(serializers.ModelSerializer):
    """ 
    Serializer for creating and displaying polls with nested options.
    """
    options = OptionSerializer(many=True)
    created_at = serializers.StringRelatedField(read_only=True)
    total_votes = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = [
                  'id', 'title', 'description', 'created_by',
                  'is_active', 'allow_multiple_votes', 'created_at',
                  'expires_at', 'options', 'total_votes', 'is_expired'
        ]
        read_only_fields = ['id', 'created_by', 'created_at',]
        
    def get_total_votes(self, obj):
        """Get total vote count for this poll."""
        return obj.votes.count()
        
    def get_is_expired(self, obj):
        """Check if the poll is expired."""
        return obj.is_expired()
        
    def validate_options(self, value):
        """
        Ensure at least 2 options are provided.
        """
        if len(value) < 2:
            raise serializers.ValidationError(
                "A poll must have at least 2 options."
            )
        return value
    
    def validate_expires_at(self, value):
        """
        Ensure expiry date is in the future.
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiry date must be in the future."
            )
        return value
    
    def create(self, validated_data):
        """
        Create poll with nested options.
        """
        options_data = validated_data.pop('options')
        
        # Create the poll
        poll = Poll.objects.create(**validated_data)
        
        # Create the options
        for option_data in options_data:
            Option.objects.create(poll=poll, **option_data)
        
        return poll
    
    def update(self, instance, validated_data):
        """
        Update poll (options cannot be updated if votes exist).
        """
        options_data = validated_data.pop('options', None)
        
        # Update poll fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.expires_at = validated_data.get('expires_at', instance.expires_at)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        
        return instance
        
        
class PollListSerializer(serializers.ModelSerializer):
    """ 
    Lightweight serializer for poll list view.
    Shows basic info without all options details.
    """
    created_by = serializers.StringRelatedField(read_only=True)
    options_count = serializers.SerializerMethodField(read_only=True)
    total_votes = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by',
            'is_active', 'created_at', 'expires_at',
            'options_count', 'total_votes'
        ]
        read_only_fields = ['id', 'created_at', 'options_count', 'total_votes']
        
    def get_options_count(self, obj):
        """Get number of options for this poll."""
        return obj.options.count()
    
    def get_total_votes(self, obj):
        """Get total vote count for this poll."""
        return obj.votes.count()
    
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates password strength and ensures passwords match.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        """
        Check that passwords match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password.
        """
        validated_data.pop('password2')  # Remove password2, not needed for creation
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']  # create_user automatically hashes
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile display.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    
class VoteSerializer(serializers.Serializer):
    """
    Serializer for casting votes.
    
    Only needs option_id as input. Poll ID comes from URL.
    voter_identifier is automatically determined (IP or user ID).
    """
    option_id = serializers.IntegerField()
    
    def validate_option_id(self, value):
        """
        Ensure the option exists.
        """
        try:
            Option.objects.get(id=value)
        except Option.DoesNotExist:
            raise serializers.ValidationError("Invalid option ID.")
        return value
    
    
    def validate(self, attrs):
        """
        Ensure the option belongs to the poll being voted on.
        """
        option_id = attrs['option_id']
        poll_id = self.context.get('poll_id')
        
        try:
            option = Option.objects.get(id=option_id)
            if option.poll_id != poll_id:
                raise serializers.ValidationError(
                    "This option does not belong to this poll."
                )
        except Option.DoesNotExist:
            raise serializers.ValidationError("Invalid option.")
        
        return attrs


class PollResultSerializer(serializers.Serializer):
    """
    Serializer for poll results display.
    Shows vote counts and percentages for each option.
    """
    option = serializers.CharField()
    votes = serializers.IntegerField()
    percentage = serializers.FloatField()