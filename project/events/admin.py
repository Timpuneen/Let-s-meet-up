from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from django.utils.html import format_html
from .models import Event


@admin.register(Event)
class EventAdmin(ModelAdmin):
    """Admin panel for Event model with Unfold and soft delete support"""
    list_display = ['title', 'organizer', 'date', 'location', 'participants_count', 'status_badge', 'created_at']
    list_filter = ['date', 'created_at', 'is_deleted']
    search_fields = ['title', 'description', 'organizer__email', 'organizer__name']
    date_hierarchy = 'date'
    ordering = ['-date']
    filter_horizontal = ['participants']
    actions = ['restore_selected', 'hard_delete_selected']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'location', 'organizer')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Status', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def get_queryset(self, request):
        """Show all events including soft-deleted ones in admin"""
        return Event.all_objects.all().select_related('organizer').prefetch_related('participants')
    
    @display(description='Participants', ordering='participants')
    def participants_count(self, obj):
        return obj.participants.count()
    
    @display(description='Status', ordering='is_deleted')
    def status_badge(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Deleted</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
        )
    
    @action(description='Restore selected events')
    def restore_selected(self, request, queryset):
        """Restore soft-deleted events"""
        count = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                count += 1
        self.message_user(request, f'{count} event(s) restored successfully.')
    
    @action(description='Permanently delete selected events')
    def hard_delete_selected(self, request, queryset):
        """Permanently delete events from database"""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f'{count} event(s) permanently deleted.')