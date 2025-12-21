from typing import Dict

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter
from unfold.decorators import display

from .models import (
    FRIENDSHIP_STATUS_ACCEPTED,
    FRIENDSHIP_STATUS_PENDING,
    FRIENDSHIP_STATUS_REJECTED,
    Friendship,
)


ADMIN_URL_USER_CHANGE = '/admin/users/user/{}/change/'

COLOR_STATUS_PENDING = '#f59e0b'
COLOR_STATUS_ACCEPTED = '#22c55e'
COLOR_STATUS_REJECTED = '#ef4444'
COLOR_STATUS_DEFAULT = '#6b7280'
COLOR_LINK_PRIMARY = '#8b5cf6'

STATUS_BADGE_STYLE = 'background:{};color:white;padding:4px 10px;border-radius:10px;font-size:11px;'
LINK_STYLE = f'color:{COLOR_LINK_PRIMARY};'

DATE_FORMAT = '%b %d, %Y'


@admin.register(Friendship)
class FriendshipAdmin(ModelAdmin):
    """Admin interface for friendships."""
    
    list_display = [
        'sender_link',
        'receiver_link',
        'status_badge',
        'created_date',
    ]
    
    list_filter = [
        'status',
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'sender__email',
        'sender__name',
        'receiver__email',
        'receiver__name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['sender', 'receiver']

    @display(description=_('Sender'), ordering='sender__email')
    def sender_link(self, obj: Friendship) -> SafeString:
        """
        Display sender as link to user admin page.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            SafeString: HTML formatted link to sender.
        """
        return format_html(
            '<a href="{}" style="{}">{}</a>',
            ADMIN_URL_USER_CHANGE.format(obj.sender.pk),
            LINK_STYLE,
            obj.sender.name or obj.sender.email
        )

    @display(description=_('Receiver'), ordering='receiver__email')
    def receiver_link(self, obj: Friendship) -> SafeString:
        """
        Display receiver as link to user admin page.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            SafeString: HTML formatted link to receiver.
        """
        return format_html(
            '<a href="{}" style="{}">{}</a>',
            ADMIN_URL_USER_CHANGE.format(obj.receiver.pk),
            LINK_STYLE,
            obj.receiver.name or obj.receiver.email
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj: Friendship) -> SafeString:
        """
        Display status as colored badge.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            SafeString: HTML formatted status badge.
        """
        status_colors: Dict[str, str] = {
            FRIENDSHIP_STATUS_PENDING: COLOR_STATUS_PENDING,
            FRIENDSHIP_STATUS_ACCEPTED: COLOR_STATUS_ACCEPTED,
            FRIENDSHIP_STATUS_REJECTED: COLOR_STATUS_REJECTED,
        }
        return format_html(
            '<span style="{}">{}</span>',
            STATUS_BADGE_STYLE.format(status_colors.get(obj.status, COLOR_STATUS_DEFAULT)),
            obj.get_status_display()
        )

    @display(description=_('Created'), ordering='created_at')
    def created_date(self, obj: Friendship) -> str:
        """
        Display formatted creation date.
        
        Args:
            obj: Friendship instance.
            
        Returns:
            str: Formatted date string.
        """
        return obj.created_at.strftime(DATE_FORMAT)