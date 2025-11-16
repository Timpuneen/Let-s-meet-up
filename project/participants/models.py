"""
Participant models for event registration and management.

This module contains models for managing event participants,
their status, and administrative privileges.
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from abstracts.models import AbstractTimestampedModel


# Constants for participant status choices
PARTICIPANT_STATUS_PENDING = 'pending'
PARTICIPANT_STATUS_ACCEPTED = 'accepted'
PARTICIPANT_STATUS_REJECTED = 'rejected'
PARTICIPANT_STATUS_CANCELLED = 'cancelled'

PARTICIPANT_STATUS_CHOICES = [
    (PARTICIPANT_STATUS_PENDING, 'Pending'),
    (PARTICIPANT_STATUS_ACCEPTED, 'Accepted'),
    (PARTICIPANT_STATUS_REJECTED, 'Rejected'),
    (PARTICIPANT_STATUS_CANCELLED, 'Cancelled'),
]


class EventParticipant(AbstractTimestampedModel):
    """
    Model representing a user's participation in an event.
    
    Manages the relationship between users and events, including
    participation status, admin privileges, and invitation tracking.
    
    Attributes:
        event (Event): The event being participated in.
        user (User): The participating user.
        status (str): Current status of the participation.
        is_admin (bool): Whether the user has admin privileges for this event.
        invited_by (User): User who invited this participant (optional).
        created_at (datetime): When participation was created (from AbstractTimestampedModel).
        updated_at (datetime): When participation was last updated (from AbstractTimestampedModel).
    """
    
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='participants_rel',
        verbose_name='Event',
        help_text='Event being participated in',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_participations',
        verbose_name='User',
        help_text='Participating user',
    )
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS_CHOICES,
        default=PARTICIPANT_STATUS_PENDING,
        verbose_name='Status',
        help_text='Current status of the participation',
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name='Is Admin',
        help_text='Whether this user has admin privileges for the event',
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations',
        verbose_name='Invited By',
        help_text='User who invited this participant',
    )
    
    class Meta:
        db_table = 'events_participants'
        verbose_name = 'Event Participant'
        verbose_name_plural = 'Event Participants'
        ordering = ['-created_at']
        unique_together = [['event', 'user']]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['invited_by']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the participation.
        
        Returns:
            str: User name and event title.
        """
        return f"{self.user.name} - {self.event.title} ({self.status})"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed participation information.
        """
        return (
            f"EventParticipant(event_id={self.event_id}, user_id={self.user_id}, "
            f"status={self.status}, is_admin={self.is_admin})"
        )
    
    def clean(self) -> None:
        """
        Validate the participant instance.
        
        Ensures that:
        - Event is not full (if max_participants is set).
        - User is not the organizer (organizer is automatically a participant).
        - Event is not deleted.
        
        Raises:
            ValidationError: If validation fails.
        """
        if self.event.is_deleted:
            raise ValidationError('Cannot participate in a deleted event')
        
        if self.user == self.event.organizer:
            raise ValidationError('Organizer is automatically a participant')
        
        # Check capacity only for new accepted participants
        if (self.status == PARTICIPANT_STATUS_ACCEPTED and 
            self.pk is None and 
            self.event.is_full()):
            raise ValidationError('Event has reached maximum capacity')
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the participant instance after validation.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    def accept(self) -> None:
        """
        Accept the participation request.
        
        Changes status to 'accepted' and saves the instance.
        
        Raises:
            ValidationError: If event is full.
        """
        if self.event.is_full():
            raise ValidationError('Event has reached maximum capacity')
        
        self.status = PARTICIPANT_STATUS_ACCEPTED
        self.save(update_fields=['status', 'updated_at'])
    
    def reject(self) -> None:
        """
        Reject the participation request.
        
        Changes status to 'rejected' and saves the instance.
        """
        self.status = PARTICIPANT_STATUS_REJECTED
        self.save(update_fields=['status', 'updated_at'])
    
    def cancel(self) -> None:
        """
        Cancel the participation.
        
        Changes status to 'cancelled' and saves the instance.
        """
        self.status = PARTICIPANT_STATUS_CANCELLED
        self.save(update_fields=['status', 'updated_at'])
    
    def make_admin(self) -> None:
        """
        Grant admin privileges to this participant.
        
        Raises:
            ValidationError: If participant is not accepted.
        """
        if self.status != PARTICIPANT_STATUS_ACCEPTED:
            raise ValidationError('Only accepted participants can be made admin')
        
        self.is_admin = True
        self.save(update_fields=['is_admin', 'updated_at'])
    
    def remove_admin(self) -> None:
        """
        Remove admin privileges from this participant.
        """
        self.is_admin = False
        self.save(update_fields=['is_admin', 'updated_at'])