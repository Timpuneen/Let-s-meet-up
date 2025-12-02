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
    """Admin interface for event participants (accepted members only)."""
    
    list_display = [
        'event_link',
        'user_link',
        'is_admin_badge',
        'joined_date',
    ]
    
    list_filter = [
        'is_admin',
        ('event', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'event__title',
        'user__email',
        'user__name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at', 'status']
    
    autocomplete_fields = ['event', 'user']
    
    fieldsets = (
        (_('Participation Details'), {
            'fields': ('event', 'user', 'is_admin'),
            'description': 'Manage confirmed event participants',
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )
    
    actions = [
        'make_admin',
        'remove_admin',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('event', 'user')

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

    @display(description=_('Role'), ordering='is_admin')
    def is_admin_badge(self, obj):
        if obj.is_admin:
            return format_html(
                '<span style="background:#3b82f6;color:white;padding:4px 10px;border-radius:10px;font-size:11px;font-weight:500;">👑 Admin</span>'
            )
        return format_html(
            '<span style="background:#e5e7eb;color:#374151;padding:4px 10px;border-radius:10px;font-size:11px;">Member</span>'
        )

    @display(description=_('Joined'), ordering='created_at')
    def joined_date(self, obj):
        from django.utils import timezone
        now = timezone.now()
        delta = now - obj.created_at
        
        if delta.days == 0:
            return format_html('<span style="color:#22c55e;">Today</span>')
        elif delta.days < 7:
            return format_html('<span style="color:#f59e0b;">{} days ago</span>', delta.days)
        else:
            return obj.created_at.strftime('%b %d, %Y')

    @admin.action(description=_('Grant admin privileges'))
    def make_admin(self, request, queryset):
        """Grant admin privileges to selected participants."""
        updated = 0
        for participant in queryset.filter(is_admin=False):
            participant.make_admin()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} participant(s) granted admin privileges.',
            level='success'
        )

    @admin.action(description=_('Remove admin privileges'))
    def remove_admin(self, request, queryset):
        """Remove admin privileges from selected participants."""
        updated = 0
        for participant in queryset.filter(is_admin=True):
            participant.remove_admin()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} participant(s) admin privileges removed.',
            level='success'
        )