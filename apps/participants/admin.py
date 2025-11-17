"""Admin configuration for participant models."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED, PARTICIPANT_STATUS_REJECTED


@admin.register(EventParticipant)
class EventParticipantAdmin(ModelAdmin):
    """
    Admin interface for EventParticipant model.
    
    Provides list display, search, filtering, and actions
    for managing event participants.
    """
    
    list_display = [
        'user',
        'event',
        'status',
        'is_admin',
        'invited_by',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__name',
        'event__title',
        'invited_by__email',
        'invited_by__name',
    ]
    list_filter = ['status', 'is_admin', 'created_at', 'event']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['event', 'user', 'invited_by']
    
    actions = ['accept_participants', 'reject_participants', 'make_admin', 'remove_admin']
    
    def accept_participants(self, request, queryset):
        """
        Admin action to accept selected participants.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventParticipant instances.
        """
        updated = 0
        for participant in queryset:
            try:
                participant.accept()
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error accepting {participant}: {str(e)}',
                    level='error'
                )
        
        if updated > 0:
            self.message_user(request, f'{updated} participant(s) accepted.')
    
    accept_participants.short_description = 'Accept selected participants'
    
    def reject_participants(self, request, queryset):
        """
        Admin action to reject selected participants.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventParticipant instances.
        """
        updated = queryset.update(status=PARTICIPANT_STATUS_REJECTED)
        self.message_user(request, f'{updated} participant(s) rejected.')
    
    reject_participants.short_description = 'Reject selected participants'
    
    def make_admin(self, request, queryset):
        """
        Admin action to grant admin privileges to selected participants.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventParticipant instances.
        """
        accepted = queryset.filter(status=PARTICIPANT_STATUS_ACCEPTED)
        updated = accepted.update(is_admin=True)
        self.message_user(request, f'{updated} participant(s) made admin.')
    
    make_admin.short_description = 'Make selected participants admin'
    
    def remove_admin(self, request, queryset):
        """
        Admin action to remove admin privileges from selected participants.
        
        Args:
            request: HttpRequest object.
            queryset: Selected EventParticipant instances.
        """
        updated = queryset.update(is_admin=False)
        self.message_user(request, f'{updated} participant(s) removed from admin.')
    
    remove_admin.short_description = 'Remove admin from selected participants'