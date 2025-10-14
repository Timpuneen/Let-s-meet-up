from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin panel for Event model"""
    list_display = ['title', 'organizer', 'date', 'participants_count', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'description', 'organizer__email']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participants'
