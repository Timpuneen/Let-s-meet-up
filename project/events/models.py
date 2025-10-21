from django.db import models
from django.conf import settings

from abstracts.models import AbstractSoftDeletableModel


class Event(AbstractSoftDeletableModel):
    """
    Event model with soft delete functionality.
    - title: event title
    - description: description
    - date: event date and time
    - location: event location
    - organizer: organizer (ForeignKey to User)
    - participants: participants (ManyToMany to User)
    - is_deleted: soft delete flag (inherited)
    - deleted_at: timestamp of deletion (inherited)
    """
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    date = models.DateTimeField(verbose_name='Event date and time')
    location = models.CharField(max_length=255, blank=True, default='', verbose_name='Location')
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Organizer'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='registered_events',
        blank=True,
        verbose_name='Participants'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f"Event(title={self.title}, description={self.description}, date={self.date}, organizer={self.organizer}, participants={self.participants.count()})"
