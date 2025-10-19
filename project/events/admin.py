from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Event


@admin.register(Event)
class EventAdmin(ModelAdmin):
    """Admin panel for Event model with Unfold"""
    list_display = ['title', 'organizer', 'date', 'participants_count', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'description', 'organizer__email', 'organizer__name']
    date_hierarchy = 'date'
    ordering = ['-date']
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'location', 'organizer')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    @display(description='Participants', ordering='participants')
    def participants_count(self, obj):
        return obj.participants.count()
