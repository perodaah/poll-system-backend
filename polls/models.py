from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Poll(models.Model):
    """
    Represents a poll/survey with a question.
    
    A poll can have multiple options (choices) and can be voted on by users.
    Polls can be set to expire after a certain date.
    """
    title = models.CharField(
        max_length=200,
        help_text="The main question being asked in the poll"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional detailed description of the poll"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='polls',
        null=True,
        blank=True,
        help_text="User who created this poll (optional for anonymous polls)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this poll is currently accepting votes"
    )
    allow_multiple_votes = models.BooleanField(
        default=False,
        help_text="Allow users to vote multiple times on this poll"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this poll was created"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this poll stops accepting votes (optional)"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest polls first
        indexes = [
            models.Index(fields=['is_active']),  # Fast filtering of active polls
            models.Index(fields=['expires_at']),  # Fast expiry checks
            models.Index(fields=['-created_at']),  # Fast ordering by date
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """
        Validation: Ensure expires_at is in the future.
        """
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiry date must be in the future")
    
    def is_expired(self):
        """
        Check if poll has expired.
        """
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-deactivate expired polls.
        """
        if self.is_expired():
            self.is_active = False
        super().save(*args, **kwargs)
        
        
class Option(models.Model):
    """
    Represents a choice/option for a poll.
    
    Each poll must have at least 2 options for users to vote on.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="The poll this option belongs to"
    )
    text = models.CharField(
        max_length=200,
        help_text="The text of this option/choice"
    )
    order_index = models.PositiveIntegerField(
        default=0,
        help_text="Display order of this option"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_index', 'id']  # Ordered by order_index, then by ID
        indexes = [
            models.Index(fields=['poll']),  # Fast lookup of poll's options
        ]
        unique_together = [['poll', 'order_index']]  # No duplicate order within same poll
    
    def __str__(self):
        return f"{self.poll.title} - {self.text}"


class Vote(models.Model):
    """
    Represents a single vote on a poll option.
    
    Tracks who voted (by IP or user ID) to prevent duplicate voting.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="The poll this vote belongs to"
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="The option that was voted for"
    )
    voter_identifier = models.CharField(
        max_length=255,
        help_text="IP address or user ID to prevent duplicate votes"
    )
    voted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this vote was cast"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['poll', 'voter_identifier']),  # Fast duplicate check
            models.Index(fields=['option']),  # Fast vote counting per option
        ]
        # CRITICAL: Prevents duplicate voting
        # If allow_multiple_votes is False, this constraint ensures one vote per person per poll
        constraints = [
            models.UniqueConstraint(
                fields=['poll', 'voter_identifier'],
                name='unique_vote_per_poll',
                violation_error_message='You have already voted on this poll'
            )
        ]
    
    def __str__(self):
        return f"Vote on {self.poll.title} for {self.option.text}"
    
    def clean(self):
        """
        Validation: Ensure option belongs to the poll.
        """
        if self.option.poll != self.poll:
            raise ValidationError("Option does not belong to this poll")