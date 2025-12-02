# apps/friendships/admin.py
"""
Admin configuration for Friendship model.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RangeDateTimeFilter

from .models import Friendship


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
    def sender_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.sender.pk,
            obj.sender.name or obj.sender.email
        )

    @display(description=_('Receiver'), ordering='receiver__email')
    def receiver_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.receiver.pk,
            obj.receiver.name or obj.receiver.email
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'accepted': '#22c55e',
            'rejected': '#ef4444',
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;font-size:11px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )

    @display(description=_('Created'), ordering='created_at')
    def created_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
