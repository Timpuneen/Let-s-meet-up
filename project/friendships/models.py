"""
Friendship models for managing user relationships.

This module contains models for handling friend requests
and friendship status between users.
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from abstracts.models import AbstractTimestampedModel


# Constants for friendship status choices
FRIENDSHIP_STATUS_PENDING = 'pending'
FRIENDSHIP_STATUS_ACCEPTED = 'accepted'
FRIENDSHIP_STATUS_REJECTED = 'rejected'
FRIENDSHIP_STATUS_BLOCKED = 'blocked'

FRIENDSHIP_STATUS_CHOICES = [
    (FRIENDSHIP_STATUS_PENDING, 'Pending'),
    (FRIENDSHIP_STATUS_ACCEPTED, 'Accepted'),
    (FRIENDSHIP_STATUS_REJECTED, 'Rejected'),
    (FRIENDSHIP_STATUS_BLOCKED, 'Blocked'),
]


class Friendship(AbstractTimestampedModel):
    """
    Friendship model for managing relationships between users.
    
    Represents a directed relationship from sender to receiver.
    When status is 'accepted', the friendship is mutual.
    
    Attributes:
        sender (User): User who initiated the friendship request.
        receiver (User): User who received the friendship request.
        status (str): Current status of the friendship.
        created_at (datetime): When the friendship was created (from AbstractTimestampedModel).
        updated_at (datetime): When the friendship was last updated (from AbstractTimestampedModel).
    """
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friendships',
        verbose_name='Sender',
        help_text='User who initiated the friendship request',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friendships',
        verbose_name='Receiver',
        help_text='User who received the friendship request',
    )
    status = models.CharField(
        max_length=20,
        choices=FRIENDSHIP_STATUS_CHOICES,
        default=FRIENDSHIP_STATUS_PENDING,
        verbose_name='Status',
        help_text='Current status of the friendship',
    )
    
    class Meta:
        db_table = 'friendships'
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'
        ordering = ['-created_at']
        unique_together = [['sender', 'receiver']]
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the friendship.
        
        Returns:
            str: Friendship description.
        """
        return f"{self.sender.name} → {self.receiver.name} ({self.status})"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the friendship.
        
        Returns:
            str: Detailed friendship information.
        """
        return f"Friendship(sender={self.sender.email}, receiver={self.receiver.email}, status={self.status})"
    
    def clean(self) -> None:
        """
        Validate the friendship instance.
        
        Ensures that:
        - Sender and receiver are different users.
        - No duplicate friendships exist in opposite direction.
        
        Raises:
            ValidationError: If validation fails.
        """
        if self.sender == self.receiver:
            raise ValidationError('Users cannot be friends with themselves')
        
        # Check for existing friendship in opposite direction
        if self.pk is None:  # Only check on creation
            opposite_exists = Friendship.objects.filter(
                sender=self.receiver,
                receiver=self.sender
            ).exists()
            
            if opposite_exists:
                raise ValidationError(
                    'A friendship request already exists in the opposite direction'
                )
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the friendship instance after validation.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    def accept(self) -> None:
        """
        Accept the friendship request.
        
        Changes status to 'accepted' and saves the instance.
        """
        self.status = FRIENDSHIP_STATUS_ACCEPTED
        self.save(update_fields=['status', 'updated_at'])
    
    def reject(self) -> None:
        """
        Reject the friendship request.
        
        Changes status to 'rejected' and saves the instance.
        """
        self.status = FRIENDSHIP_STATUS_REJECTED
        self.save(update_fields=['status', 'updated_at'])
    
    def block(self) -> None:
        """
        Block the user.
        
        Changes status to 'blocked' and saves the instance.
        """
        self.status = FRIENDSHIP_STATUS_BLOCKED
        self.save(update_fields=['status', 'updated_at'])
    
    @classmethod
    def are_friends(cls, user1, user2) -> bool:
        """
        Check if two users are friends.
        
        Args:
            user1: First user.
            user2: Second user.
        
        Returns:
            bool: True if users are friends, False otherwise.
        """
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2) | models.Q(sender=user2, receiver=user1),
            status=FRIENDSHIP_STATUS_ACCEPTED
        ).exists()
    
    @classmethod
    def get_friends(cls, user):
        """
        Get all friends of a user.
        
        Args:
            user: User instance.
        
        Returns:
            QuerySet: User objects who are friends with the given user.
        """
        from users.models import User
        
        # Get all accepted friendships where user is either sender or receiver
        friendships = cls.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user),
            status=FRIENDSHIP_STATUS_ACCEPTED
        )
        
        # Extract friend IDs
        friend_ids = []
        for friendship in friendships:
            if friendship.sender == user:
                friend_ids.append(friendship.receiver_id)
            else:
                friend_ids.append(friendship.sender_id)
        
        return User.objects.filter(id__in=friend_ids)