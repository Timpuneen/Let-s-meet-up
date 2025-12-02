"""
Admin configuration for EventComment model.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventComment


@admin.register(EventComment)
class EventCommentAdmin(ModelAdmin):
    """Admin interface for event comments."""
    
    list_display = [
        'comment_preview',
        'user_link',
        'event_link',
        'has_parent',
        'created_date',
    ]
    
    list_filter = [
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'content',
        'user__email',
        'user__name',
        'event__title',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['event', 'user', 'parent']
    
    @display(description=_('Comment'), header=True)
    def comment_preview(self, obj):
        preview = obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
        return [
            format_html('<span style="color:#374151;">{}</span>', preview)
        ]


    @display(description=_('User'), ordering='user__email')
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.user.pk,
            obj.user.name or obj.user.email
        )

    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.event.pk,
            obj.event.title
        )

    @display(description=_('Reply'), ordering='parent')
    def has_parent(self, obj):
        if obj.parent:
            return format_html('<span style="color:#f59e0b;">↳ Reply</span>')
        return format_html('<span style="color:#22c55e;">● Original</span>')

    @display(description=_('Posted'), ordering='created_at')
    def created_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y %H:%M')

