from django.conf import settings
from django.db import models, connection
from django.core.exceptions import ValidationError

from apps.abstracts.models import AbstractTimestampedModel
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED


INVITATION_STATUS_MAX_LENGTH = 20

INVITATION_STATUS_PENDING = 'pending'
INVITATION_STATUS_ACCEPTED = 'accepted'
INVITATION_STATUS_REJECTED = 'rejected'

INVITATION_STATUS_CHOICES = [
    (INVITATION_STATUS_PENDING, 'Pending'),
    (INVITATION_STATUS_ACCEPTED, 'Accepted'),
    (INVITATION_STATUS_REJECTED, 'Rejected'),
]


class EventInvitation(AbstractTimestampedModel):
    """
    Model representing an invitation to an event.
    
    Manages invitations sent to users for events, tracking who sent
    the invitation and the current status.
    
    Attributes:
        event (Event): The event for which invitation was sent.
        invited_user (User): The user who received the invitation.
        invited_by (User): User who sent the invitation.
        status (str): Current status of the invitation.
        created_at (datetime): When invitation was created (from AbstractTimestampedModel).
        updated_at (datetime): When invitation was last updated (from AbstractTimestampedModel).
    """
    
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Event',
        help_text='Event for which invitation was sent',
    )
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_invitations',
        verbose_name='Invited User',
        help_text='User who received the invitation',
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_event_invitations',
        verbose_name='Invited By',
        help_text='User who sent the invitation',
    )
    status = models.CharField(
        max_length=INVITATION_STATUS_MAX_LENGTH,
        choices=INVITATION_STATUS_CHOICES,
        default=INVITATION_STATUS_PENDING,
        verbose_name='Status',
        help_text='Current status of the invitation',
    )
    
    class Meta:
        db_table = 'event_invitations'
        verbose_name = 'Event Invitation'
        verbose_name_plural = 'Event Invitations'
        ordering = ['-created_at']
        unique_together = [['event', 'invited_user']]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['invited_user', 'status']),
            models.Index(fields=['invited_by']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the invitation.
        
        Returns:
            str: Invited user name and event title.
        """
        return f"{self.invited_user.name} invited to {self.event.title} ({self.status})"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed invitation information.
        """
        return (
            f"EventInvitation(event_id={self.event_id}, "
            f"invited_user_id={self.invited_user_id}, "
            f"invited_by_id={self.invited_by_id}, status={self.status})"
        )
    
    def clean(self) -> None:
        """
        Validate the invitation instance.
        
        Ensures that:
        - Event is not deleted.
        - User is not the organizer.
        - User is not already a participant (только для pending инвайтов).
        - Invited_by has permission to invite.
        
        Raises:
            ValidationError: If validation fails.
        """
        if self.event.is_deleted:
            raise ValidationError('Cannot invite to a deleted event')
        
        if self.invited_user == self.event.organizer:
            raise ValidationError('Cannot invite the organizer')
        
        if self.status == INVITATION_STATUS_PENDING:
            if EventParticipant.objects.filter(
                event=self.event,
                user=self.invited_user
            ).exists():
                raise ValidationError('User is already a participant of this event')
        
        if not self.event.can_user_invite(self.invited_by):
            raise ValidationError('You do not have permission to invite users to this event')
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the invitation instance after validation.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    def accept(self) -> None:
        """
        Accept the invitation and create participant record.
        
        Changes status to 'accepted', creates EventParticipant, and saves.
        
        Raises:
            ValidationError: If event is full or already accepted.
        """
        if self.status == INVITATION_STATUS_ACCEPTED:
            raise ValidationError('Invitation already accepted')
        
        if self.event.is_full():
            raise ValidationError('Event has reached maximum capacity')
                
        if EventParticipant.objects.filter(
            event=self.event,
            user=self.invited_user
        ).exists():
            self.status = INVITATION_STATUS_ACCEPTED
            super(EventInvitation, self).save(update_fields=['status', 'updated_at'])
            return
        
        EventParticipant.objects.create(
            event=self.event,
            user=self.invited_user,
            status=PARTICIPANT_STATUS_ACCEPTED,
            is_admin=False,
        )
        
        self.status = INVITATION_STATUS_ACCEPTED
                
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE event_invitations SET status = %s, updated_at = NOW() WHERE id = %s",
                [INVITATION_STATUS_ACCEPTED, self.id]
            )
        
    def reject(self) -> None:
        """
        Reject the invitation.
        
        Changes status to 'rejected' and saves the instance.
        """
        self.status = INVITATION_STATUS_REJECTED
        self.save(update_fields=['status', 'updated_at'])