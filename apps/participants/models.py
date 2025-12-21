from typing import Any

from django.conf import settings
from django.db.models import ForeignKey, CharField, BooleanField, Index, CASCADE
from django.core.exceptions import ValidationError

from apps.abstracts.models import AbstractTimestampedModel

PARTICIPANT_STATUS_ACCEPTED = 'accepted'

PARTICIPANT_STATUS_CHOICES = [
    (PARTICIPANT_STATUS_ACCEPTED, 'Accepted'),
]

PARTICIPANT_STATUS_MAX_LENGTH = 20

ADMIN_UPDATE_FIELDS = ['is_admin', 'updated_at']

class EventParticipant(AbstractTimestampedModel):
    """
    Model representing a user's participation in an event.
    
    Manages the relationship between users and events for confirmed participants only.
    Invitations are now handled by the EventInvitation model.
    
    Attributes:
        event (Event): The event being participated in.
        user (User): The participating user.
        status (str): Current status (always 'accepted' for participants).
        is_admin (bool): Whether the user has admin privileges for this event.
        created_at (datetime): When participation was created (from AbstractTimestampedModel).
        updated_at (datetime): When participation was last updated (from AbstractTimestampedModel).
    """
    
    event: 'Event' = ForeignKey(
        'events.Event',
        on_delete=CASCADE,
        related_name='participants_rel',
        verbose_name='Event',
        help_text='Event being participated in',
    )

    user: 'User' = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='event_participations',
        verbose_name='User',
        help_text='Participating user',
    )

    status: CharField = CharField(
        max_length=PARTICIPANT_STATUS_MAX_LENGTH,
        choices=PARTICIPANT_STATUS_CHOICES,
        default=PARTICIPANT_STATUS_ACCEPTED,
        verbose_name='Status',
        help_text='Current status of the participation (always accepted)',
    )

    is_admin: BooleanField = BooleanField(
        default=False,
        verbose_name='Is Admin',
        help_text='Whether this user has admin privileges for the event',
    )
    
    class Meta:
        db_table = 'events_participants'
        verbose_name = 'Event Participant'
        verbose_name_plural = 'Event Participants'
        ordering = ['-created_at']
        unique_together = [['event', 'user']]
        indexes = [
            Index(fields=['event', 'status']),
            Index(fields=['user', 'status']),
            Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the participation.
        
        Returns:
            str: User name and event title.
        """
        return f"{self.user.name} - {self.event.title}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed participation information.
        """
        return (
            f"EventParticipant(event_id={self.event_id}, user_id={self.user_id}, "
            f"is_admin={self.is_admin})"
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
        
        if self.pk is None and self.event.is_full():
            raise ValidationError('Event has reached maximum capacity')
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the participant instance after validation and enforce accepted status."""
        self.status = PARTICIPANT_STATUS_ACCEPTED
        self.full_clean()
        super().save(*args, **kwargs)
    
    def make_admin(self) -> None:
        """
        Grant admin privileges to this participant.
        """
        self.is_admin = True
        self.save(update_fields=ADMIN_UPDATE_FIELDS)
    
    def remove_admin(self) -> None:
        """
        Remove admin privileges from this participant.
        """
        self.is_admin = False
        self.save(update_fields=ADMIN_UPDATE_FIELDS)