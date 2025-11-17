"""Admin configuration for friendship models."""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Friendship, FRIENDSHIP_STATUS_ACCEPTED, FRIENDSHIP_STATUS_REJECTED


@admin.register(Friendship)
class FriendshipAdmin(ModelAdmin):
    """
    Admin interface for Friendship model.
    
    Provides list display, search, filtering, and actions
    for managing friendships.
    """
    
    list_display = ['sender', 'receiver', 'status', 'created_at', 'updated_at']
    search_fields = ['sender__email', 'sender__name', 'receiver__email', 'receiver__name']
    list_filter = ['status', 'created_at', 'updated_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['sender', 'receiver']
    
    actions = ['accept_friendships', 'reject_friendships']
    
    def accept_friendships(self, request, queryset):
        """
        Admin action to accept selected friendship requests.
        
        Args:
            request: HttpRequest object.
            queryset: Selected Friendship instances.
        """
        updated = queryset.update(status=FRIENDSHIP_STATUS_ACCEPTED)
        self.message_user(request, f'{updated} friendship(s) accepted.')
    
    accept_friendships.short_description = 'Accept selected friendships'
    
    def reject_friendships(self, request, queryset):
        """
        Admin action to reject selected friendship requests.
        
        Args:
            request: HttpRequest object.
            queryset: Selected Friendship instances.
        """
        updated = queryset.update(status=FRIENDSHIP_STATUS_REJECTED)
        self.message_user(request, f'{updated} friendship(s) rejected.')
    
    reject_friendships.short_description = 'Reject selected friendships'