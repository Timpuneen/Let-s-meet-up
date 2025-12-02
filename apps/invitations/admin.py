"""
Admin configuration for Event Invitations.

This module contains admin interface customization for managing
event invitations through Django admin panel.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import EventInvitation


@admin.register(EventInvitation)
class EventInvitationAdmin(ModelAdmin):
    """
    Admin interface for EventInvitation model.
    
    Provides filtering, searching, and custom display
    for managing invitations in the admin panel.
    """
    
    list_display = [
        'id',
        'display_event',
        'display_invited_user',
        'display_invited_by',
        'display_status',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'event__status',
    ]
    
    search_fields = [
        'event__title',
        'invited_user__name',
        'invited_user__email',
        'invited_by__name',
        'invited_by__email',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    autocomplete_fields = [
        'event',
        'invited_user',
        'invited_by',
    ]
    
    ordering = ['-created_at']
    
    list_per_page = 25
    
    fieldsets = [
        ('Invitation Details', {
            'fields': [
                'event',
                'invited_user',
                'invited_by',
                'status',
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at',
            ],
            'classes': ['collapse'],
        }),
    ]
    
    @display(description='Event', ordering='event__title')
    def display_event(self, obj):
        """Display event title with link."""
        return obj.event.title
    
    @display(description='Invited User', ordering='invited_user__name')
    def display_invited_user(self, obj):
        """Display invited user name with email."""
        return f"{obj.invited_user.name} ({obj.invited_user.email})"
    
    @display(description='Invited By', ordering='invited_by__name')
    def display_invited_by(self, obj):
        """Display inviter name with email."""
        return f"{obj.invited_by.name} ({obj.invited_by.email})"
    
    @display(description='Status', ordering='status')
    def display_status(self, obj):
        """Display status with colored badge."""
        colors = {
            'pending': '#FFA500',  # Orange
            'accepted': '#28A745',  # Green
            'rejected': '#DC3545',  # Red
        }
        color = colors.get(obj.status, '#6C757D')
        return f'<span style="color: {color}; font-weight: bold;">● {obj.get_status_display()}</span>'
    
    def has_add_permission(self, request):
        """
        Disable manual creation through admin.
        
        Invitations should be created through API to ensure
        proper validation and permission checks.
        """
        return False