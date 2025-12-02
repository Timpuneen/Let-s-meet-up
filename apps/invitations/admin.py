from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter, RangeDateTimeFilter

from .models import EventInvitation


@admin.register(EventInvitation)
class EventInvitationAdmin(ModelAdmin):
    """Enhanced admin interface for Event Invitations."""
    
    list_display = [
        'event_link',
        'invited_user_link',
        'invited_by_link',
        'status_badge',
        'invitation_date',
    ]
    
    list_filter = [
        'status',
        ('event', RelatedDropdownFilter),
        ('invited_by', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    
    search_fields = [
        'event__title',
        'invited_user__email',
        'invited_user__name',
        'invited_by__email',
        'invited_by__name',
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['event', 'invited_user', 'invited_by']
    
    fieldsets = (
        (_('Invitation Details'), {
            'fields': ('event', 'invited_user', 'invited_by', 'status'),
            'description': 'Manage event invitation details',
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse'],
        }),
    )
    
    actions = [
        'accept_invitations',
        'reject_invitations',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('event', 'invited_user', 'invited_by')

    
    @display(description=_('Event'), ordering='event__title')
    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:#8b5cf6;font-weight:500;">{}</a>',
            obj.event.pk,
            obj.event.title
        )

    @display(description=_('Invited User'), ordering='invited_user__email')
    def invited_user_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#8b5cf6;">{}</a>',
            obj.invited_user.pk,
            obj.invited_user.name or obj.invited_user.email
        )

    @display(description=_('Invited By'), ordering='invited_by__email')
    def invited_by_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/" style="color:#6b7280;">{}</a>',
            obj.invited_by.pk,
            obj.invited_by.name or obj.invited_by.email
        )

    @display(description=_('Status'), ordering='status')
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'accepted': '#22c55e',
            'rejected': '#ef4444',
        }
        icons = {
            'pending': '⏳',
            'accepted': '✓',
            'rejected': '✗',
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:10px;font-size:11px;font-weight:500;">{} {}</span>',
            colors.get(obj.status, '#6b7280'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )

    @display(description=_('Invited On'), ordering='created_at')
    def invitation_date(self, obj):
        from django.utils import timezone
        now = timezone.now()
        delta = now - obj.created_at
        
        if delta.days == 0:
            color = '#22c55e'
            text = 'Today'
        elif delta.days < 7:
            color = '#f59e0b'
            text = f'{delta.days}d ago'
        else:
            color = '#9ca3af'
            text = obj.created_at.strftime('%b %d, %Y')
        
        return format_html(
            '<span style="color:{};">{}</span>',
            color,
            text
        )

    
    @admin.action(description=_('Accept selected invitations'))
    def accept_invitations(self, request, queryset):
        """Bulk accept invitations."""
        success_count = 0
        error_count = 0
        
        for invitation in queryset.filter(status='pending'):
            try:
                invitation.accept()
                success_count += 1
            except Exception as e:
                error_count += 1
        
        if success_count:
            self.message_user(
                request,
                f'{success_count} invitation(s) accepted successfully.',
                level='success'
            )
        if error_count:
            self.message_user(
                request,
                f'{error_count} invitation(s) could not be accepted.',
                level='warning'
            )

    @admin.action(description=_('Reject selected invitations'))
    def reject_invitations(self, request, queryset):
        """Bulk reject invitations."""
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(
            request,
            f'{updated} invitation(s) rejected.',
            level='success'
        )