from django.db import models
from django.utils.text import slugify

from apps.abstracts.models import AbstractTimestampedModel


class Category(AbstractTimestampedModel):
    """
    Category model for event classification.
    
    Provides a taxonomy for organizing events into different types
    (e.g., Sports, Music, Technology, etc.).
    
    Attributes:
        name (str): Human-readable category name.
        slug (str): URL-friendly identifier for the category.
        created_at (datetime): Creation timestamp (from AbstractTimestampedModel).
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Category Name',
        help_text='Human-readable name of the category',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Slug',
        help_text='URL-friendly identifier for the category',
    )
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the category.
        
        Returns:
            str: Category name.
        """
        return self.name
    
    def __repr__(self) -> str:
        """
        Return detailed string representation of the category.
        
        Returns:
            str: Detailed category information.
        """
        return f"Category(name={self.name}, slug={self.slug})"
    
    def save(self, *args, **kwargs) -> None:
        """
        Save the category instance.
        
        Automatically generates a slug from the name if not provided.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class EventCategory(AbstractTimestampedModel):
    """
    Through model for the many-to-many relationship between Events and Categories.
    
    Allows tracking when events were assigned to categories
    and potentially adding additional metadata in the future.
    
    Attributes:
        event (Event): Foreign key to the event.
        category (Category): Foreign key to the category.
        created_at (datetime): When this relationship was created (from AbstractTimestampedModel).
    """
    
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='event_categories',
        verbose_name='Event',
        help_text='Event being categorized',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='event_categories',
        verbose_name='Category',
        help_text='Category assigned to the event',
    )
    
    class Meta:
        db_table = 'event_categories'
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'
        ordering = ['event', 'category']
        unique_together = [['event', 'category']]
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self) -> str:
        """
        Return string representation of the event-category relationship.
        
        Returns:
            str: Event title and category name.
        """
        return f"{self.event.title} - {self.category.name}"
    
    def __repr__(self) -> str:
        """
        Return detailed string representation.
        
        Returns:
            str: Detailed relationship information.
        """
        return f"EventCategory(event_id={self.event_id}, category_id={self.category_id})"