"""
Event models for managing meetup events.

This module contains the Event model with soft delete functionality,
geographical references, and various event management features.
"""

from django.conf import settings
from django.db import models

from apps.abstracts.models import AbstractSoftDeletableModel, AbstractTimestampedModel, SoftDeletableManager

from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


# Constants for event status choices
EVENT_STATUS_DRAFT = 'draft'
EVENT_STATUS_PUBLISHED = 'published'
EVENT_STATUS_CANCELLED = 'cancelled'
EVENT_STATUS_COMPLETED = 'completed'

EVENT_STATUS_CHOICES = [
    (EVENT_STATUS_DRAFT, 'Draft'),
    (EVENT_STATUS_PUBLISHED, 'Published'),
    (EVENT_STATUS_CANCELLED, 'Cancelled'),
    (EVENT_STATUS_COMPLETED, 'Completed'),
]


# Constants for invitation permission choices
INVITATION_PERM_ORGANIZER = 'organizer'
INVITATION_PERM_ADMINS = 'admins'
INVITATION_PERM_PARTICIPANTS = 'participants'

INVITATION_PERM_CHOICES = [
    (INVITATION_PERM_ORGANIZER, 'Organizer Only'),
    (INVITATION_PERM_ADMINS, 'Admins Only'),
    (INVITATION_PERM_PARTICIPANTS, 'All Participants'),
]


class Event(AbstractSoftDeletableModel, AbstractTimestampedModel):
    """
    Event model with soft delete functionality.
    
    Represents a meetup event with all necessary information including
    location, participants, status, and invitation settings.
    
    Attributes:
        title (str): Event title.
        description (str): Event description.
        address (str): Physical address of the event.
        date (datetime): Event date and time.
        status (str): Current status of the event.
        invitation_perm (str): Who can invite others to this event.
        max_participants (int): Maximum number of participants (null = unlimited).
        organizer (User): Event organizer.
        country (Country): Country where event takes place.
        city (City): City where event takes place.
        categories (Category): Event categories (many-to-many through EventCategory).
        is_deleted (bool): Soft delete flag (from AbstractSoftDeletableModel).
        deleted_at (datetime): Deletion timestamp (from AbstractSoftDeletableModel).
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
        updated_at (datetime): Last update timestamp (from AbstractTimestampedModel).
    """
    
    title = models.CharField(
        max_length=255,
        verbose_name='Title',
        help_text='Event title',
    )
    description = models.TextField(
        verbose_name='Description',
        help_text='Detailed event description',
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Address',
        help_text='Physical address of the event venue',
        null=True,
        blank=True
    )
    date = models.DateTimeField(
        verbose_name='Event Date and Time',
        help_text='When the event will take place',
    )
    status = models.CharField(
        max_length=50,
        choices=EVENT_STATUS_CHOICES,
        default=EVENT_STATUS_PUBLISHED,
        verbose_name='Status',
        help_text='Current status of the event',
    )
    invitation_perm = models.CharField(
        max_length=50,
        choices=INVITATION_PERM_CHOICES,
        default=INVITATION_PERM_PARTICIPANTS,
        verbose_name='Invitation Permission',
        help_text='Who can invite others to this event',
    )
    max_participants = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Max Participants',
        help_text='Maximum number of participants (leave empty for unlimited)',
    )
    
    # Relationships
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Organizer',
        help_text='User who created and manages this event',
    )
    country = models.ForeignKey(
        'geography.Country',
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name='Country',
        help_text='Country where the event takes place',
        null=True,
        blank=True
    )
    city = models.ForeignKey(
        'geography.City',
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name='City',
        help_text='City where the event takes place',
        null=True,
        blank=True
    )
    categories = models.ManyToManyField(
        'categories.Category',
        through='categories.EventCategory',
        related_name='events',
        verbose_name='Categories',
        help_text='Categories this event belongs to',
    )
    
    objects = SoftDeletableManager() 

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status', 'date']),
            models.Index(fields=['organizer', 'date']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['is_deleted', 'status']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the event.
        
        Returns:
            str: Event title.
        """
        return self.title
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the event.
        
        Returns:
            str: Detailed event information.
        """
        return (
            f"Event(title={self.title}, date={self.date}, "
            f"organizer={self.organizer.email}, status={self.status})"
        )
    
    def get_participants_count(self) -> int:
        """
        Get the number of accepted participants.
        
        Returns:
            int: Number of participants with accepted status.
        """
        return self.participants_rel.filter(status=PARTICIPANT_STATUS_ACCEPTED).count()
    
    def is_full(self) -> bool:
        """
        Check if the event has reached maximum capacity.
        
        Returns:
            bool: True if event is full, False otherwise.
        """
        if self.max_participants is None:
            return False
        return self.get_participants_count() >= self.max_participants
    
    def can_user_invite(self, user) -> bool:
        """
        Check if a user can invite others to this event.
        
        Args:
            user: User instance to check permissions for.
        
        Returns:
            bool: True if user can invite, False otherwise.
        """
        if user == self.organizer:
            return True
        
        if self.invitation_perm == INVITATION_PERM_ORGANIZER:
            return False
        
        try:
            participant = self.participants_rel.get(user=user, status=PARTICIPANT_STATUS_ACCEPTED)
            
            if self.invitation_perm == INVITATION_PERM_ADMINS:
                return participant.is_admin
            
            return True  # INVITATION_PERM_PARTICIPANTS
        except EventParticipant.DoesNotExist:
            return False