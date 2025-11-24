from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Event

@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ['title', 'organizer', 'date', 'status', 'city', 'country', 'created_at']
    search_fields = ['title', 'description', 'organizer__email', 'organizer__name']
    list_filter = ['status', 'country', 'city', 'date', 'created_at']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['organizer', 'country', 'city']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'organizer')
        }),
        ('Location', {
            'fields': ('country', 'city', 'address')
        }),
        ('Schedule', {
            'fields': ('date', 'status')
        }),
        ('Settings', {
            'fields': ('invitation_perm', 'max_participants')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )