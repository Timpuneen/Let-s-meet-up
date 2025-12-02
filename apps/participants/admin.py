"""
Admin configuration for EventParticipant model.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventParticipant


@admin.register(EventParticipant)
class EventParticipantAdmin(ModelAdmin):
    """Admin interface for event participants."""
    
    list_display = [
        'event_link',
        'user_link',
        'status_badge',
        'is_admin_badge',
        'invited_by_link',
        'joined_date',
    ]
    
    list_filter = [
        'status',
        'is_admin',
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'event__title',
        'user__email',
        'user__name',
        'invited_by__email',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['event', 'user', 'invited_by']
    
    fieldsets = (
        (_('Participation Details'), {
            'fields': ('event', 'user', 'status', 'is_admin'),
        }),
        (_('Invitation'), {
            'fields': ('invited_by',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:#8b5cf6;font-weight:500;">{}</a>',
            obj.event.pk,
            obj.event.title
        )

    @display(description=_('User'), ordering='user__email')
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.user.pk,
            obj.user.name or obj.user.email
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'accepted': '#22c55e',
            'rejected': '#ef4444',
            'cancelled': '#6b7280',
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;font-size:11px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )

    @display(description=_('Admin'), ordering='is_admin')
    def is_admin_badge(self, obj):
        if obj.is_admin:
            return format_html('<span style="color:#3b82f6;font-weight:600;">✓ Admin</span>')
        return format_html('<span style="color:#9ca3af;">Member</span>')

    @display(description=_('Invited By'))
    def invited_by_link(self, obj):
        if obj.invited_by:
            return format_html(
                '<a href="/admin/users/user/{}/change/" style="color:#6b7280;">{}</a>',
                obj.invited_by.pk,
                obj.invited_by.name or obj.invited_by.email
            )
        return '-'

    @display(description=_('Joined'), ordering='created_at')
    def joined_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
