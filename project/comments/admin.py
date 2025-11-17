"""Admin configuration for comment models."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import EventComment


@admin.register(EventComment)
class EventCommentAdmin(ModelAdmin):
    """
    Admin interface for EventComment model.
    
    Provides list display, search, filtering, and hierarchical
    viewing for managing event comments.
    """
    
    list_display = [
        'id',
        'user',
        'event',
        'content_preview',
        'parent',
        'depth_indicator',
        'reply_count',
        'created_at',
    ]
    search_fields = [
        'content',
        'user__email',
        'user__name',
        'event__title',
    ]
    list_filter = ['created_at', 'event']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'depth_level', 'total_replies']
    autocomplete_fields = ['event', 'user', 'parent']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('event', 'user', 'parent')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('depth_level', 'total_replies')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj: EventComment) -> str:
        """
        Display a truncated version of the comment content.
        
        Args:
            obj: EventComment instance.
        
        Returns:
            str: Truncated comment content.
        """
        max_length = 60
        if len(obj.content) > max_length:
            return obj.content[:max_length] + '...'
        return obj.content
    
    content_preview.short_description = 'Content'
    
    def depth_indicator(self, obj: EventComment) -> str:
        """
        Display visual indicator of comment depth.
        
        Args:
            obj: EventComment instance.
        
        Returns:
            str: Visual representation of nesting level.
        """
        depth = obj.get_depth()
        return '→ ' * depth + f'Level {depth}'
    
    depth_indicator.short_description = 'Depth'
    
    def reply_count(self, obj: EventComment) -> int:
        """
        Display the number of replies to this comment.
        
        Args:
            obj: EventComment instance.
        
        Returns:
            int: Number of replies.
        """
        return obj.get_reply_count()
    
    reply_count.short_description = 'Replies'
    
    def depth_level(self, obj: EventComment) -> int:
        """
        Display the depth level in readonly field.
        
        Args:
            obj: EventComment instance.
        
        Returns:
            int: Depth level.
        """
        return obj.get_depth()
    
    depth_level.short_description = 'Thread Depth'
    
    def total_replies(self, obj: EventComment) -> int:
        """
        Display the total number of replies in readonly field.
        
        Args:
            obj: EventComment instance.
        
        Returns:
            int: Total replies count.
        """
        return obj.get_reply_count()
    
    total_replies.short_description = 'Total Replies'