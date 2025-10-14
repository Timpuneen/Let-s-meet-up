from django.db import models
from django.conf import settings


class Event(models.Model):
    """
    Event model
    - title: event title
    - description: description
    - date: event date and time
    - organizer: organizer (ForeignKey to User)
    - participants: participants (ManyToMany to User)
    """
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    date = models.DateTimeField(verbose_name='Event date and time')
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
