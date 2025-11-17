"""Admin configuration for media models."""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import EventPhoto


@admin.register(EventPhoto)
class EventPhotoAdmin(ModelAdmin):
    """
    Admin interface for EventPhoto model.
    
    Provides list display, search, filtering, and actions
    for managing event photos.
    """
    
    list_display = [
        'thumbnail',
        'event',
        'uploaded_by',
        'is_cover',
        'caption_preview',
        'created_at',
    ]
    search_fields = [
        'event__title',
        'uploaded_by__email',
        'uploaded_by__name',
        'caption',
    ]
    list_filter = ['is_cover', 'created_at', 'event']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'thumbnail_large']
    autocomplete_fields = ['event', 'uploaded_by']
    
    actions = ['set_as_cover', 'remove_as_cover']
    
    fieldsets = (
        ('Photo Information', {
            'fields': ('event', 'uploaded_by', 'url', 'thumbnail_large')
        }),
        ('Details', {
            'fields': ('caption', 'is_cover')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail(self, obj: EventPhoto) -> str:
        """
        Display a small thumbnail of the photo.
        
        Args:
            obj: EventPhoto instance.
        
        Returns:
            str: HTML for displaying thumbnail.
        """
        return format_html(
            '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
            obj.url
        )
    
    thumbnail.short_description = 'Thumbnail'
    
    def thumbnail_large(self, obj: EventPhoto) -> str:
        """
        Display a larger preview of the photo.
        
        Args:
            obj: EventPhoto instance.
        
        Returns:
            str: HTML for displaying large preview.
        """
        return format_html(
            '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" />',
            obj.url
        )
    
    thumbnail_large.short_description = 'Preview'
    
    def caption_preview(self, obj: EventPhoto) -> str:
        """
        Display a truncated version of the caption.
        
        Args:
            obj: EventPhoto instance.
        
        Returns:
            str: Truncated caption or empty string.
        """
        if obj.caption:
            return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
        return '-'
    
    caption_preview.short_description = 'Caption'
    
    def set_as_cover(self, request, queryset):
        """
        Admin action to set selected photo as cover.
        
        Only works if a single photo is selected.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventPhoto instances.
        """
        if queryset.count() != 1:
            self.message_user(
                request,
                'Please select exactly one photo to set as cover.',
                level='error'
            )
            return
        
        photo = queryset.first()
        photo.set_as_cover()
        self.message_user(request, f'Photo set as cover for {photo.event.title}.')
    
    set_as_cover.short_description = 'Set as cover photo'
    
    def remove_as_cover(self, request, queryset):
        """
        Admin action to remove cover status from selected photos.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventPhoto instances.
        """
        updated = queryset.filter(is_cover=True).update(is_cover=False)
        self.message_user(request, f'{updated} photo(s) removed as cover.')
    
    remove_as_cover.short_description = 'Remove as cover photo'