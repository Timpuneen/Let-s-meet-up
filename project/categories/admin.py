"""Admin configuration for category models."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, EventCategory


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Admin interface for Category model.
    
    Provides list display, search, and filtering capabilities
    for managing categories.
    """
    
    list_display = ['name', 'slug', 'events_count', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['created_at']
    ordering = ['name']
    readonly_fields = ['slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    
    def events_count(self, obj: Category) -> int:
        """
        Get the number of events in this category.
        
        Args:
            obj: Category instance.
        
        Returns:
            int: Number of events.
        """
        return obj.event_categories.count()
    
    events_count.short_description = 'Events'


@admin.register(EventCategory)
class EventCategoryAdmin(ModelAdmin):
    """
    Admin interface for EventCategory model.
    
    Provides list display, search, and filtering capabilities
    for managing event-category relationships.
    """
    
    list_display = ['event', 'category', 'created_at']
    search_fields = ['event__title', 'category__name']
    list_filter = ['category', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['event', 'category']