"""
Media models for event photos and attachments.

This module contains models for managing photos uploaded to events,
including cover images and captions.
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from abstracts.models import AbstractTimestampedModel, AbstractSoftDeletableModel, SoftDeletableManager


class EventPhoto(AbstractTimestampedModel, AbstractSoftDeletableModel):
    """
    Model representing a photo uploaded to an event.
    
    Stores photo metadata and references, including who uploaded it,
    captions, and whether it's the cover photo for the event.
    
    Attributes:
        event (Event): The event this photo belongs to.
        uploaded_by (User): User who uploaded the photo.
        url (str): URL or path to the photo file.
        caption (str): Optional caption describing the photo.
        is_cover (bool): Whether this photo is the event's cover image.
        created_at (datetime): When photo was uploaded (from AbstractTimestampedModel).
    """
    
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Event',
        help_text='Event this photo belongs to',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_photos',
        verbose_name='Uploaded By',
        help_text='User who uploaded this photo',
    )
    url = models.CharField(
        max_length=500,
        verbose_name='Photo URL',
        help_text='URL or path to the photo file',
    )
    caption = models.TextField(
        null=True,
        blank=True,
        verbose_name='Caption',
        help_text='Optional caption describing the photo',
    )
    is_cover = models.BooleanField(
        default=False,
        verbose_name='Is Cover Photo',
        help_text='Whether this photo is the event cover image',
    )
    
    objects = SoftDeletableManager()

    class Meta:
        db_table = 'event_photos'
        verbose_name = 'Event Photo'
        verbose_name_plural = 'Event Photos'
        ordering = ['-is_cover', '-created_at']
        indexes = [
            models.Index(fields=['event', 'is_cover']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the photo.
        
        Returns:
            str: Event title and photo type.
        """
        photo_type = 'Cover Photo' if self.is_cover else 'Photo'
        return f"{self.event.title} - {photo_type}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed photo information.
        """
        return (
            f"EventPhoto(event_id={self.event_id}, uploaded_by_id={self.uploaded_by_id}, "
            f"is_cover={self.is_cover})"
        )
    
    def clean(self) -> None:
        """
        Validate the photo instance.
        
        Ensures that:
        - Only one cover photo exists per event.
        - User has permission to upload photos to the event.
        
        Raises:
            ValidationError: If validation fails.
        """
        # Check if trying to set as cover when another cover exists
        if self.is_cover:
            existing_cover = EventPhoto.objects.filter(
                event=self.event,
                is_cover=True
            ).exclude(pk=self.pk)
            
            if existing_cover.exists():
                raise ValidationError(
                    'Another cover photo already exists for this event. '
                    'Remove the existing cover first.'
                )
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the photo instance after validation.
        
        If this photo is being set as cover, automatically
        removes cover status from other photos.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if self.is_cover:
            # Remove cover status from other photos
            EventPhoto.objects.filter(
                event=self.event,
                is_cover=True
            ).exclude(pk=self.pk).update(is_cover=False)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def set_as_cover(self) -> None:
        """
        Set this photo as the event's cover photo.
        
        Automatically removes cover status from other photos.
        """
        self.is_cover = True
        self.save(update_fields=['is_cover'])
    
    def remove_as_cover(self) -> None:
        """
        Remove cover status from this photo.
        """
        self.is_cover = False
        self.save(update_fields=['is_cover'])