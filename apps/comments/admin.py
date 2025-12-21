from typing import List

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter, RelatedDropdownFilter
from unfold.decorators import display

from .models import EventComment


ADMIN_URL_USER_CHANGE = '/admin/users/user/{}/change/'
ADMIN_URL_EVENT_CHANGE = '/admin/events/event/{}/change/'

COLOR_PRIMARY = '#8b5cf6'
COLOR_WARNING = '#f59e0b'
COLOR_SUCCESS = '#22c55e'
COLOR_GRAY_DARK = '#374151'

COMMENT_PREVIEW_LENGTH = 60
DATE_FORMAT = '%b %d, %Y %H:%M'


@admin.register(EventComment)
class EventCommentAdmin(ModelAdmin):
    """Admin interface for event comments."""
    
    list_display = [
        'comment_preview',
        'user_link',
        'event_link',
        'has_parent',
        'created_date',
    ]
    
    list_filter = [
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'content',
        'user__email',
        'user__name',
        'event__title',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['event', 'user', 'parent']
    
    @display(description=_('Comment'), header=True)
    def comment_preview(self, obj: EventComment) -> List[SafeString]:
        """
        Display comment preview (truncated to 60 characters).
        
        Args:
            obj: EventComment instance.
            
        Returns:
            List[SafeString]: HTML formatted comment preview.
        """
        preview = obj.content[:COMMENT_PREVIEW_LENGTH] + '...' if len(obj.content) > COMMENT_PREVIEW_LENGTH else obj.content
        return [
            format_html('<span style="color:{};">{}</span>', COLOR_GRAY_DARK, preview)
        ]

    @display(description=_('User'), ordering='user__email')
    def user_link(self, obj: EventComment) -> SafeString:
        """
        Display user as link to user admin page.
        
        Args:
            obj: EventComment instance.
            
        Returns:
            SafeString: HTML formatted link to user.
        """
        return format_html(
            '<a href="{}" style="color:{};">{}</a>',
            ADMIN_URL_USER_CHANGE.format(obj.user.pk),
            COLOR_PRIMARY,
            obj.user.name or obj.user.email
        )

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj: EventComment) -> SafeString:
        """
        Display event as link to event admin page.
        
        Args:
            obj: EventComment instance.
            
        Returns:
            SafeString: HTML formatted link to event.
        """
        return format_html(
            '<a href="{}" style="color:{};">{}</a>',
            ADMIN_URL_EVENT_CHANGE.format(obj.event.pk),
            COLOR_PRIMARY,
            obj.event.title
        )

    @display(description=_('Reply'), ordering='parent')
    def has_parent(self, obj: EventComment) -> SafeString:
        """
        Display whether comment is a reply or original.
        
        Args:
            obj: EventComment instance.
            
        Returns:
            SafeString: HTML formatted reply indicator.
        """
        if obj.parent:
            return format_html('<span style="color:{};">↳ Reply</span>', COLOR_WARNING)
        return format_html('<span style="color:{};">● Original</span>', COLOR_SUCCESS)

    @display(description=_('Posted'), ordering='created_at')
    def created_date(self, obj: EventComment) -> str:
        """
        Display formatted creation date.
        
        Args:
            obj: EventComment instance.
            
        Returns:
            str: Formatted date string.
        """
        return obj.created_at.strftime(DATE_FORMAT)